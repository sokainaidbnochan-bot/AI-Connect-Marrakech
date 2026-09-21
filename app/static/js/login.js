const pull = document.getElementById("pull");
const glow = document.getElementById("glow");
const beam = document.getElementById("beam");
const card = document.getElementById("loginCard");
let lit = false;

pull.addEventListener("click", () => {
  lit = !lit;
  glow.style.opacity = lit ? "0.55" : "0";
  beam.style.opacity = lit ? "1" : "0";
  card.classList.toggle("visible", lit);
});