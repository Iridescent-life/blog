(function () {
  var selector = "textarea.rich-text-editor";

  function loadScript(src, onLoad) {
    var script = document.createElement("script");
    script.src = src;
    script.referrerPolicy = "no-referrer";
    script.onload = onLoad;
    document.head.appendChild(script);
  }

  function initEditor() {
    if (!window.tinymce) {
      return;
    }

    window.tinymce.init({
      selector: selector,
      height: 480,
      menubar: false,
      branding: false,
      promotion: false,
      convert_urls: false,
      relative_urls: false,
      plugins: "link lists code table image autoresize",
      toolbar:
        "undo redo | blocks | bold italic underline strikethrough | forecolor backcolor | " +
        "alignleft aligncenter alignright | bullist numlist outdent indent | link image table | code",
      content_style: "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 15px; }"
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (!document.querySelector(selector)) {
      return;
    }

    if (window.tinymce) {
      initEditor();
      return;
    }

    loadScript("https://cdn.jsdelivr.net/npm/tinymce@7.9.0/tinymce.min.js", initEditor);
  });
})();
