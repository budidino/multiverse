
function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName + 'View').style.display = "block";
    evt.currentTarget.className += " active";

    localStorage.setItem('tab', tabName);
}

// Open last opened tab
function loaded() {
    if (localStorage.getItem('tab') === null) {
        localStorage.setItem('tab', 'Competition');
    }
    document.getElementById(localStorage.getItem('tab')).click();
}
