document.addEventListener("DOMContentLoaded", function() {
    let button = document.createElement("button");
    button.innerText = "Toggle Dark Mode";
    button.style.position = "fixed";
    button.style.top = "10px";
    button.style.right = "10px";
    button.onclick = function() {
        document.body.classList.toggle("dark-mode");
    };
    document.body.prepend(button);
});
