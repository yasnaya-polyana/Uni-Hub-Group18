document.addEventListener('DOMContentLoaded', function() {
    // Initialize topics functionality
    console.log('Topics JS initialized');
    
    // Find any checkboxes with name="topics"
    let topicCheckboxes = document.querySelectorAll('input[type="checkbox"][name="topics"]');
    
    if (topicCheckboxes.length > 0) {
        console.log('Found', topicCheckboxes.length, 'topic checkboxes');
        
        // Add a simple event listener to log when checkboxes are clicked
        topicCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                console.log('Topic changed:', this.value, 'Selected:', this.checked);
                // The actual handling of these checkboxes is done server-side
            });
        });
    } else {
        console.log('No topic checkboxes found on this page');
    }
}); 