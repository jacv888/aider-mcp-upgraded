document.addEventListener("DOMContentLoaded", () => {
  // Smooth scrolling for navigation links
  const navLinks = document.querySelectorAll('a[href^="#"]');
  navLinks.forEach(link => {
    link.addEventListener("click", e => {
      e.preventDefault();
      const targetId = link.getAttribute("href").substring(1);
      const targetElement = document.getElementById(targetId);
      if (targetElement) {
        targetElement.scrollIntoView({ behavior: "smooth" });
      }
      // Close mobile menu if open
      if (mobileMenu.classList.contains("active")) {
        toggleMobileMenu();
      }
    });
  });

  // Animated counters
  const counters = document.querySelectorAll(".counter");
  const speed = 200; // lower is faster

  const animateCounter = (counter) => {
    const updateCount = () => {
      const target = +counter.getAttribute("data-target");
      const count = +counter.innerText;
      const increment = Math.ceil(target / speed);

      if (count < target) {
        counter.innerText = count + increment > target ? target : count + increment;
        requestAnimationFrame(updateCount);
      } else {
        counter.innerText = target;
      }
    };
    updateCount();
  };

  const countersSection = document.querySelector("#counters");
  let countersAnimated = false;

  const onScroll = () => {
    if (!countersAnimated && countersSection) {
      const rect = countersSection.getBoundingClientRect();
      if (rect.top < window.innerHeight && rect.bottom >= 0) {
        counters.forEach(animateCounter);
        countersAnimated = true;
        window.removeEventListener("scroll", onScroll);
      }
    }
  };
  window.addEventListener("scroll", onScroll);

  // Form validation
  const form = document.querySelector("form");
  if (form) {
    form.addEventListener("submit", e => {
      e.preventDefault();
      const inputs = form.querySelectorAll("input[required], textarea[required]");
      let valid = true;
      inputs.forEach(input => {
        if (!input.value.trim()) {
          valid = false;
          input.classList.add("input-error");
        } else {
          input.classList.remove("input-error");
        }
        if (input.type === "email" && input.value) {
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!emailRegex.test(input.value)) {
            valid = false;
            input.classList.add("input-error");
          }
        }
      });
      if (valid) {
        form.submit();
      } else {
        const errorMsg = form.querySelector(".form-error-message");
        if (errorMsg) {
          errorMsg.style.display = "block";
        }
      }
    });
  }

  // Mobile menu toggle
  const mobileMenuButton = document.querySelector(".mobile-menu-button");
  const mobileMenu = document.querySelector(".mobile-menu");

  const toggleMobileMenu = () => {
    mobileMenu.classList.toggle("active");
    mobileMenuButton.classList.toggle("active");
  };

  if (mobileMenuButton && mobileMenu) {
    mobileMenuButton.addEventListener("click", toggleMobileMenu);
  }
});
