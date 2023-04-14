function follow(event){
    a = event.target
    follow_id = a.dataset.follow_id
    console.log(a)
    fetch('/user/follow/'+follow_id, {method:'POST'}).then( function() {
        followButton = document.getElementById('buttonfollow-'+follow_id);
        followButton.innerHTML = 'Followed ✓';
        followButton.disabled = true;
        followButton.style.background ='green'
    });

};

function unfollow(event){
    a = event.target
    unfollow_id = a.dataset.unfollow_id
    console.log(a)
    fetch('/user/unfollow/'+unfollow_id, {method:'POST'}).then( function() {
        unfollowButton = document.getElementById('buttonunfollow-'+unfollow_id);
        unfollowButton.innerHTML = 'Un-Followed ✓';
        unfollowButton.style.background ='green'
        unfollowButton.disabled = true;
    });

};