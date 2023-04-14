

//side bar
const menuItems = document.querySelectorAll('.menu-item');

// remove active from all menu-items
const changeActiveItem = () => {
    menuItems.forEach(item =>{
        item.classList.remove('active')
    });
};

menuItems.forEach(item => {
    item.addEventListener('click', ()=>{
        changeActiveItem();
        item.classList.add('active');
    });
});


