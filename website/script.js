// ===== הגדרות – יש להחליף במספר האמיתי (פורמט בינלאומי, ללא + וללא 0 בהתחלה) =====
const WHATSAPP_NUMBER = "972500000000";

// תפריט מובייל
const toggle = document.querySelector(".menu-toggle");
const nav = document.getElementById("nav");
toggle.addEventListener("click", () => {
  const open = nav.classList.toggle("open");
  toggle.setAttribute("aria-expanded", open);
});
nav.querySelectorAll("a").forEach((a) =>
  a.addEventListener("click", () => {
    nav.classList.remove("open");
    toggle.setAttribute("aria-expanded", "false");
  })
);

// טופס יצירת קשר – פותח וואטסאפ עם ההודעה
document.getElementById("contact-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const data = new FormData(e.target);
  const text =
    `שלום, אשמח לקבוע שיחת היכרות.\n` +
    `שם: ${data.get("name")}\n` +
    `טלפון: ${data.get("phone")}` +
    (data.get("message") ? `\n${data.get("message")}` : "");
  window.open(`https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(text)}`, "_blank");
});

// שנה בתחתית
document.getElementById("year").textContent = new Date().getFullYear();

// אנימציית כניסה עדינה לסקשנים
const observer = new IntersectionObserver(
  (entries) =>
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    }),
  { threshold: 0.12 }
);
document.querySelectorAll(".section-head, .card, .steps li, .about, .contact, .faq details")
  .forEach((el) => {
    el.classList.add("reveal");
    observer.observe(el);
  });
