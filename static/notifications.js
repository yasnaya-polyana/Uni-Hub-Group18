$(document).ready(function() {
    var notificationsLoaded = false;
    var previousUnreadCount = 0; // Variable to store the previous unread notifications count

    // Function to update unread notifications count
    function updateUnreadNotificationsCount() {
        $.ajax({
            url: '/get_unread_notifications_count/',
            method: 'GET',
            success: function(data) {
                $('#notifications-count').text(data.unread_count);
                // Check if the unread notifications count has changed
                if (data.unread_count !== previousUnreadCount) {
                    notificationsLoaded = false; // Set to false if the count has changed
                    previousUnreadCount = data.unread_count; // Update the previous unread count
                }
            },
            error: function() {
                console.error('Error fetching unread notifications count');
            }
        });
    }

    // Initial request to get unread notifications count
    updateUnreadNotificationsCount();

    // Periodically check for new notifications
    setInterval(updateUnreadNotificationsCount, 60000); // Check every 60 seconds

    $('#notifications-button').on('click', function() {
        var dropdown = $('#notifications-dropdown');
        dropdown.toggleClass('hidden');

        if (!dropdown.hasClass('hidden') && !notificationsLoaded) {
            $.ajax({
                url: '/get_notifications/',
                method: 'GET',
                success: function(data) {
                    dropdown.empty();
                    if (data.length > 0) {
                        data.forEach(function(notification) {
                            var item;
                            if (notification.type === 'like') {
                                item = $('<li><a href="' + notification.data.post_link + '" class="' + (notification.is_read ? '' : 'font-bold') + '">' + notification.data.username + ' liked your post</a></li>');
                            } else if (notification.type === 'follow') {
                                item = $('<li><a href="' + notification.data.profile_link + '" class="' + (notification.is_read ? '' : 'font-bold') + '">' + notification.data.username + ' started following you</a></li>');
                            } else {
                                item = $('<li><a href="#" class="' + (notification.is_read ? '' : 'font-bold') + '">Unknown notification type</a></li>');
                            }
                            dropdown.append(item);
                        });
                    } else {
                        dropdown.append('<li><span>No notifications</span></li>');
                    }
                    notificationsLoaded = true;
                },
                error: function() {
                    dropdown.html('<li><span>Error loading notifications</span></li>');
                }
            });
        }
    });
});