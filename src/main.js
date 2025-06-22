document.addEventListener("DOMContentLoaded", function () {
    const sections = document.querySelectorAll('.section');
  
    // Hide all sections on load
    sections.forEach(section => section.style.display = 'none');
  });
  
  // Handle navbar link clicks
  document.querySelectorAll('.navbar-link[href^="#"]').forEach(link => {
    link.addEventListener('click', function (e) {
      e.preventDefault();
  
      const targetId = this.getAttribute('href').substring(1); // e.g., 'menu', 'about'
      const sections = document.querySelectorAll('.section');
  
      // Hide all sections
      sections.forEach(section => section.style.display = 'none');
  
      // Show clicked section
      const targetSection = document.getElementById(targetId);
      if (targetSection) {
        targetSection.style.display = 'block';
        targetSection.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
