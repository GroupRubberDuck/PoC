// Sostituisce la scritta di default al nome del file aggiunto quando viene caricato

document.addEventListener("DOMContentLoaded", function() {
    const fileInput = document.getElementById('file_json');
    const fileDisplay = document.getElementById('file-name-display');

    if (fileInput && fileDisplay) {
        const defaultText = fileDisplay.textContent;

        fileInput.addEventListener('change', function(event) {
            const files = event.target.files;

            if (files && files.length > 0) {
                fileDisplay.textContent = "File pronto: " + files[0].name;
                fileDisplay.style.fontWeight = "bold";
            } else {
                fileDisplay.textContent = defaultText;
            }
        });
    }
});