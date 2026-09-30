// Procedurally builds the faint isometric "city grid" background used behind the hero
// 3D scene (blocks + parcels + two avenues + a river), approximating the original site's
// decorative SVG without hand-copying its huge generated path data.
(function () {
  const svg = document.getElementById("bg-map-svg");
  if (!svg) return;

  const NS = "http://www.w3.org/2000/svg";
  const skewY = -0.34; // isometric-ish shear
  const cols = 13, rows = 13, cell = 155, gap = 14;

  function blockPath(x0, y0, w, h) {
    const sy = (x) => x * skewY;
    const p = [
      [x0, y0 + sy(x0)],
      [x0 + w, y0 + sy(x0 + w)],
      [x0 + w, y0 + h + sy(x0 + w)],
      [x0, y0 + h + sy(x0)],
    ];
    return `M${p[0][0].toFixed(1)},${p[0][1].toFixed(1)}L${p[1][0].toFixed(1)},${p[1][1].toFixed(1)}L${p[2][0].toFixed(1)},${p[2][1].toFixed(1)}L${p[3][0].toFixed(1)},${p[3][1].toFixed(1)}Z`;
  }

  let blocks = "";
  let parcels = "";
  for (let r = -1; r < rows; r++) {
    for (let c = -1; c < cols; c++) {
      const x0 = c * (cell + gap) - 300;
      const y0 = r * (cell + gap) - 300;
      blocks += blockPath(x0, y0, cell, cell * 0.62);

      // a few finer parcel subdivisions inside each block
      const sub = 3;
      for (let i = 0; i < sub; i++) {
        for (let j = 0; j < 2; j++) {
          const pw = cell / sub - 4;
          const ph = (cell * 0.62) / 2 - 4;
          parcels += blockPath(x0 + i * (cell / sub), y0 + j * (cell * 0.31), pw, ph);
        }
      }
    }
  }

  const blockEl = document.createElementNS(NS, "path");
  blockEl.setAttribute("d", blocks);
  blockEl.setAttribute("class", "pj-map-block");
  svg.appendChild(blockEl);

  const parcelEl = document.createElementNS(NS, "path");
  parcelEl.setAttribute("d", parcels);
  parcelEl.setAttribute("class", "pj-map-parcel");
  svg.appendChild(parcelEl);

  const avenueD = "M-367.5,778.8L1980.0,279.9M746.9,-327.0L1087.9,1277.1";
  const avOuter = document.createElementNS(NS, "path");
  avOuter.setAttribute("d", avenueD);
  avOuter.setAttribute("class", "pj-map-avenue");
  svg.appendChild(avOuter);
  const avInner = document.createElementNS(NS, "path");
  avInner.setAttribute("d", avenueD);
  avInner.setAttribute("class", "pj-map-avenue-in");
  svg.appendChild(avInner);

  const river = document.createElementNS(NS, "path");
  river.setAttribute(
    "d",
    "M-60,840 C352,730 736,990 1120,870 S1660,760 1660,800 L1660,1060 L-60,1060 Z"
  );
  river.setAttribute("class", "pj-map-river");
  svg.appendChild(river);
})();
