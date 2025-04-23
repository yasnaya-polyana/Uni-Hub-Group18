import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from collections import defaultdict
import logging

from accounts.models import CustomUser
from communities.models import Communities, CommunityMember
from events.models import Event
from .models import UserInterest

logger = logging.getLogger(__name__)

def extract_user_features():
    """Extract features for each user based on their community memberships and interests"""
    users = CustomUser.objects.all()
    user_features = {}
    
    # Get all possible categories
    all_categories = list(set(Communities.objects.values_list('category', flat=True).distinct()))
    
    # If no categories exist yet, return empty data
    if not all_categories:
        logger.warning("No community categories found in the database")
        return {}, []
    
    for user in users:
        # Get communities the user is a member of
        user_communities = Communities.objects.filter(members=user)
        
        # Count categories
        category_counts = defaultdict(float)
        for community in user_communities:
            category_counts[community.category] += 1.0
        
        # Get explicit interests
        user_interests = UserInterest.objects.filter(user=user)
        for interest in user_interests:
            category_counts[interest.category] += interest.weight
        
        # Create feature vector
        features = []
        for category in sorted(all_categories):
            features.append(category_counts.get(category, 0.0))
        
        user_features[user.id] = features
    
    return user_features, sorted(all_categories)

def cluster_users(n_clusters=5):
    """Cluster users based on their features"""
    user_features, categories = extract_user_features()
    
    # If no user features, return empty data
    if not user_features:
        logger.warning("No user features available for clustering")
        return {}, np.array([]), []
    
    # Convert to numpy array
    user_ids = list(user_features.keys())
    X = np.array([user_features[uid] for uid in user_ids])
    
    # If not enough users for clustering, return simple data
    if len(user_ids) < n_clusters:
        logger.warning(f"Not enough users ({len(user_ids)}) for {n_clusters} clusters")
        n_clusters = max(1, len(user_ids))
    
    # Handle empty feature case
    if X.size == 0 or X.shape[1] == 0:
        logger.warning("Empty feature matrix, cannot perform clustering")
        return {}, np.array([]), categories
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Apply K-means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)
    
    # Map users to clusters
    user_clusters = {}
    for i, uid in enumerate(user_ids):
        user_clusters[uid] = clusters[i]
    
    return user_clusters, kmeans.cluster_centers_, categories

def get_recommendations_for_user(user, max_recommendations=3):
    """Get community and event recommendations for a specific user"""
    if not user.is_authenticated:
        return [], []
    
    try:
        user_clusters, cluster_centers, categories = cluster_users()
        
        # If clustering failed or no data
        if not user_clusters or not categories:
            logger.warning("Clustering failed or no categories available")
            return [], []
        
        # Get user's cluster
        cluster = user_clusters.get(user.id)
        if cluster is None:
            logger.warning(f"User {user.id} not found in clusters")
            return [], []
        
        # Get cluster center (preferences)
        cluster_preferences = cluster_centers[cluster]
        
        # Find top categories for this cluster
        top_categories = []
        for i, score in enumerate(cluster_preferences):
            if score > 0:  # Only consider positive preferences
                top_categories.append((categories[i], score))
        
        top_categories.sort(key=lambda x: x[1], reverse=True)
        top_categories = [c[0] for c in top_categories[:3]]  # Top 3 categories
        
        # If no top categories found, return empty
        if not top_categories:
            return [], []
        
        # Get communities the user is not a member of in those categories
        user_communities = Communities.objects.filter(members=user)
        recommended_communities = Communities.objects.filter(
            category__in=top_categories
        ).exclude(
            id__in=user_communities.values_list('id', flat=True)
        )[:max_recommendations]
        
        # Get events in those categories
        user_events = Event.objects.filter(attendees=user)
        recommended_events = Event.objects.filter(
            community__category__in=top_categories
        ).exclude(
            id__in=user_events.values_list('id', flat=True)
        )[:max_recommendations]
        
        return recommended_communities, recommended_events
    
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        return [], []