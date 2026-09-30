(function () {
  const cityEl = document.getElementById("pj-city");
  const city = window.UrbanCity ? window.UrbanCity.init(cityEl) : null;

  const pauseBtn = document.getElementById("city-pause");
  const resetBtn = document.getElementById("city-reset");
  if (pauseBtn && city) {
    pauseBtn.addEventListener("click", () => {
      const paused = city.togglePause();
      pauseBtn.setAttribute("aria-pressed", String(paused));
      pauseBtn.title = paused ? "모형 다시 움직이기" : "모형 움직임 정지";
    });
  }
  if (resetBtn && city) {
    resetBtn.addEventListener("click", () => city.reset());
  }

  const pickOnMap = document.getElementById("pick-on-map");
  if (pickOnMap) {
    pickOnMap.addEventListener("click", () => {
      alert("지도에서 선택 기능은 이 클론에서는 데모로 제공되지 않습니다.");
    });
  }

  async function handleSearch(input, alertBox) {
    const address = input.value.trim();
    if (!address) return;

    const form = input.closest("form");
    const btn = form.querySelector(".pj-go");
    const originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="pj-go-wait" aria-hidden="true"></span>';
    if (city) city.pauseFor(4000);
    if (alertBox) {
      alertBox.hidden = true;
      alertBox.textContent = "";
    }

    try {
      const res = await fetch(`/api/geocode?address=${encodeURIComponent(address)}`);
      const data = await res.json();
      btn.disabled = false;
      btn.innerHTML = originalHtml;

      if (data.ok && data.result) {
        const refined = data.result.refined ? data.result.refined.text : address;
        const point = data.result.result ? data.result.result.point : null;
        sessionStorage.setItem(
          "um-last-search",
          JSON.stringify({ query: address, refined, point, at: Date.now() })
        );
        window.location.href = `site.html?q=${encodeURIComponent(refined)}`;
      } else {
        if (alertBox) {
          alertBox.hidden = false;
          alertBox.textContent = "해당 주소를 찾을 수 없습니다. 도로명주소나 지번으로 다시 시도해 주세요.";
        } else {
          alert("해당 주소를 찾을 수 없습니다.");
        }
      }
    } catch (e) {
      btn.disabled = false;
      btn.innerHTML = originalHtml;
      if (alertBox) {
        alertBox.hidden = false;
        alertBox.textContent = "검색 중 오류가 발생했습니다. 로컬 서버(server.py)가 실행 중인지 확인해 주세요.";
      }
    }
  }

  const form1 = document.getElementById("site-search-form");
  if (form1) {
    form1.addEventListener("submit", (e) => {
      e.preventDefault();
      handleSearch(document.getElementById("pj-q"), document.getElementById("site-search-alert"));
    });
  }
  const form2 = document.getElementById("site-search-form-2");
  if (form2) {
    form2.addEventListener("submit", (e) => {
      e.preventDefault();
      handleSearch(document.getElementById("pj-q2"), null);
    });
  }
})();
