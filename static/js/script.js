document.addEventListener("DOMContentLoaded", function () {
  const textOutput = document.getElementById("text-output");
  const copyButton = document.getElementById("copy-button");
  const downloadButton = document.getElementById("download-button");

  copyButton.addEventListener("click", function () {
    // Select the text in the text box
    textOutput.select();
    textOutput.setSelectionRange(0, 99999); // For mobile devices

    // Copy the selected text to the clipboard
    navigator.clipboard.writeText(textOutput.value);

    // Alert the user that the text has been copied
    alert("Text copied to clipboard!");
  });

  downloadButton.addEventListener("click", function () {
    // Get the text from the text box
    const text = textOutput.value;

    // Create a Blob object with the text content
    const blob = new Blob([text], { type: "text/plain" });

    // Create a temporary URL for the Blob
    const url = URL.createObjectURL(blob);

    // Create a new link element
    const link = document.createElement("a");

    // Set the link's href to the temporary URL
    link.href = url;

    // Set the link's download attribute to the desired file name
    link.download = "extracted_text.txt";

    // Hide the link element
    link.style.display = "none";

    // Append the link to the document body
    document.body.appendChild(link);

    // Simulate a click on the link to trigger the download
    link.click();

    // Remove the link from the document body
    document.body.removeChild(link);

    // Revoke the temporary URL
    URL.revokeObjectURL(url);
  });
});
