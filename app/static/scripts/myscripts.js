function redirectToForm() {
    var selectedCancer = document.querySelector('input[name="cancer"]:checked');

    if (selectedCancer) {
      var cancerType = selectedCancer.value;
      window.location.href = '/' + cancerType;
    } 
}

// Get all collapsible elements
var collapsibles = document.querySelectorAll(".collapsible");

// Attach click event listeners to each collapsible
collapsibles.forEach(function(collapsible) {
    var button = collapsible.querySelector(".collapsible-button");
    var content = collapsible.querySelector(".content"); // Updated: select .content

    button.addEventListener("click", function() {
        if (content.style.display === "none" || content.style.display === "") {
            content.style.display = "block";
        } else {
            content.style.display = "none";
        }
    });
});