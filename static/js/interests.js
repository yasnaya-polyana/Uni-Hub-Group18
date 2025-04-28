document.addEventListener('DOMContentLoaded', function() {
    // Interest categories for organization
    const interestCategories = {
        'academic': [
            'Artificial Intelligence', 'Robotics', 'Software Development', 
            'Web Development', 'Data Science', 'Cybersecurity', 
            'Blockchain', 'Gaming', 'Mobile Development'
        ],
        'sports': [
            'Football', 'Basketball', 'Tennis', 
            'Swimming', 'Volleyball', 'Rugby', 
            'Athletics', 'Cycling', 'Fitness', 'Martial Arts'
        ],
        'creative': [
            'Photography', 'Music', 'Painting', 
            'Drawing', 'Writing', 'Film & Video', 'Dance', 'Theater'
        ],
        'social': [
            'Volunteering', 'Debate', 'Cultural Exchange', 
            'Entrepreneurship', 'Environmental Activism'
        ]
    };

    const interestsContainer = document.querySelector('.interests-container');
    if (!interestsContainer) return;

    const checkboxes = document.querySelectorAll('.interests-checkbox');
    const selectedInterests = new Set();

    // Initialize with already selected interests
    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            selectedInterests.add(checkbox.value);
        }
    });

    // Create the UI structure
    const container = document.createElement('div');
    container.className = 'interest-tags-container';
    
    // Add search box
    const searchBox = document.createElement('input');
    searchBox.type = 'text';
    searchBox.placeholder = 'Search interests...';
    searchBox.className = 'input input-bordered w-full interest-search';
    container.appendChild(searchBox);

    // Add category filters
    const categoriesDiv = document.createElement('div');
    categoriesDiv.className = 'interest-categories';
    
    const allCategory = document.createElement('span');
    allCategory.innerText = 'All';
    allCategory.className = 'interest-category badge badge-neutral';
    allCategory.dataset.category = 'all';
    categoriesDiv.appendChild(allCategory);
    
    for (const category in interestCategories) {
        const categoryElem = document.createElement('span');
        categoryElem.innerText = category.charAt(0).toUpperCase() + category.slice(1);
        categoryElem.className = `interest-category badge badge-outline`;
        categoryElem.dataset.category = category;
        categoriesDiv.appendChild(categoryElem);
    }
    
    container.appendChild(categoriesDiv);

    // Add tags container
    const tagsContainer = document.createElement('div');
    tagsContainer.className = 'interest-tags';
    container.appendChild(tagsContainer);

    // Add selected interests container
    const selectedContainer = document.createElement('div');
    selectedContainer.className = 'interests-selected';
    
    const selectedHeading = document.createElement('div');
    selectedHeading.className = 'interests-selected-heading';
    selectedHeading.innerText = 'Selected Interests';
    selectedContainer.appendChild(selectedHeading);
    
    const selectedTagsContainer = document.createElement('div');
    selectedTagsContainer.className = 'selected-tags';
    selectedContainer.appendChild(selectedTagsContainer);
    
    const emptyMessage = document.createElement('div');
    emptyMessage.className = 'interests-selected-empty';
    emptyMessage.innerText = 'No interests selected';
    selectedTagsContainer.appendChild(emptyMessage);
    
    container.appendChild(selectedContainer);

    // Replace the original checkboxes with our custom UI
    interestsContainer.innerHTML = '';
    interestsContainer.appendChild(container);

    // Create interest tags for all options
    let currentCategory = 'all';
    
    function createInterestTags() {
        tagsContainer.innerHTML = '';
        
        checkboxes.forEach(checkbox => {
            const label = checkbox.parentNode.textContent.trim();
            const value = checkbox.value;
            
            // Skip if not in current category
            let matchesCategory = false;
            if (currentCategory === 'all') {
                matchesCategory = true;
            } else {
                matchesCategory = interestCategories[currentCategory].includes(label);
            }
            
            // Skip if doesn't match search
            const searchTerm = searchBox.value.toLowerCase();
            const matchesSearch = label.toLowerCase().includes(searchTerm);
            
            if (matchesCategory && matchesSearch) {
                const tag = document.createElement('div');
                tag.className = 'interest-tag';
                
                // Determine category for styling
                for (const cat in interestCategories) {
                    if (interestCategories[cat].includes(label)) {
                        tag.classList.add(`interest-tag-${cat}`);
                        break;
                    }
                }
                
                tag.innerText = label;
                tag.dataset.value = value;
                
                if (selectedInterests.has(value)) {
                    tag.classList.add('selected');
                }
                
                tag.addEventListener('click', () => {
                    toggleInterest(value, label, tag);
                });
                
                tagsContainer.appendChild(tag);
            }
        });
    }
    
    function toggleInterest(value, label, tag) {
        const checkbox = document.querySelector(`.interests-checkbox[value="${value}"]`);
        
        if (selectedInterests.has(value)) {
            // Remove interest
            selectedInterests.delete(value);
            checkbox.checked = false;
            
            if (tag) tag.classList.remove('selected');
            
            // Remove from selected container
            const chip = selectedTagsContainer.querySelector(`[data-value="${value}"]`);
            if (chip) selectedTagsContainer.removeChild(chip);
            
            updateEmptyMessage();
        } else {
            // Add interest
            selectedInterests.add(value);
            checkbox.checked = true;
            
            if (tag) tag.classList.add('selected');
            
            // Add to selected container
            const chip = document.createElement('div');
            chip.className = 'interest-chip';
            chip.dataset.value = value;
            
            const chipText = document.createElement('span');
            chipText.innerText = label;
            chip.appendChild(chipText);
            
            const removeBtn = document.createElement('span');
            removeBtn.className = 'interest-chip-remove';
            removeBtn.innerHTML = '&times;';
            removeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleInterest(value, label);
            });
            chip.appendChild(removeBtn);
            
            selectedTagsContainer.appendChild(chip);
            updateEmptyMessage();
        }
    }
    
    function updateEmptyMessage() {
        if (selectedInterests.size === 0) {
            if (!selectedTagsContainer.querySelector('.interests-selected-empty')) {
                const emptyMsg = document.createElement('div');
                emptyMsg.className = 'interests-selected-empty';
                emptyMsg.innerText = 'No interests selected';
                selectedTagsContainer.appendChild(emptyMsg);
            }
        } else {
            const emptyMsg = selectedTagsContainer.querySelector('.interests-selected-empty');
            if (emptyMsg) {
                selectedTagsContainer.removeChild(emptyMsg);
            }
        }
    }

    // Initialize tags
    createInterestTags();
    
    // Update selected interests display
    checkboxes.forEach(checkbox => {
        if (checkbox.checked) {
            const label = checkbox.parentNode.textContent.trim();
            toggleInterest(checkbox.value, label);
        }
    });

    // Handle category changes
    categoriesDiv.querySelectorAll('.interest-category').forEach(cat => {
        cat.addEventListener('click', () => {
            // Update active category
            categoriesDiv.querySelectorAll('.interest-category').forEach(c => {
                c.classList.remove('badge-neutral');
                c.classList.add('badge-outline');
            });
            cat.classList.remove('badge-outline');
            cat.classList.add('badge-neutral');
            
            currentCategory = cat.dataset.category;
            createInterestTags();
        });
    });

    // Handle search
    searchBox.addEventListener('input', () => {
        createInterestTags();
    });
}); 