function DeletePost(event){
    a = event.target
    post = a.dataset.post_data
    post_div = document.getElementById('feed_post-'+post)
    let confirmation = confirm('Are you sure wants to delete this post? ')
    if (confirmation){
        fetch('/user/blog/delete/'+post, {method:'DELETE'}).then( function(){
        post_div.remove()})
        
    }
    
}
function deleteuser(event){
  a = event.target;
  user_id = a.dataset.user_id;
  let confirmation = confirm('Are you sure wants to delete your account? !!!!!! By clicking OK all your account data will be completly deleted!!!!!!')
  if (confirmation){
    button_div = document.getElementById('button-'+user_id)
    button_div.style.display = 'none'
    confirm_div = document.getElementById('delete-'+user_id)
    console.log(confirm_div)
    confirm_div.style.display = 'block'
  };
};


function like(event){
    blog = event.target
    blog_id = blog.dataset.blog_id
  
  fetch('/blog/like/'+blog_id, {method: 'POST'}).then(function() {
    // Update the like count on the page
    var likeCount = document.getElementById('like-count-'+blog_id);
    var likevar = document.getElementById('button-like-'+blog_id)
    likevar.innerHTML =  'Liked';
    likevar.style.background ='green';
    likeCount.innerHTML = parseInt(likeCount.innerHTML) + 1;
    

  });
  };

                
  function add_to_html(comment,section){
  commentsSection = document.getElementById(section); 
  commentElement = document.createElement('div');
    commentElement.classList.add('comment');
    commentElement.textContent = comment;
        // add the comment to the comments section
    commentsSection.appendChild(commentElement);
    event.target.reset();
};
    function add_comment(event){
      event.preventDefault();
      const blog = event.target;
      blog_id = blog.dataset.blog_id;
      var section = 'comments_'+blog_id
      const comment = event.target.elements.comment.value;
      fetch('/user/blog/comment/'+comment+'/id/'+blog_id,{method:'POST'}).then(
      add_to_html(comment,section))
    };
