// Minimal three.js isometric "city" scene approximating the original hero visual:
// a flat grid of light gray low-rise blocks with one highlighted blue tower, slow auto-rotate.
(function () {
  function initCity(container) {
    if (!window.THREE) return;

    const scene = new THREE.Scene();
    scene.background = null;

    const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
    camera.position.set(9, 9, 9);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    const group = new THREE.Group();
    scene.add(group);

    // ground grid plane
    const groundGeo = new THREE.PlaneGeometry(14, 14, 14, 14);
    const groundMat = new THREE.MeshBasicMaterial({ color: 0xd8dee6, wireframe: true, transparent: true, opacity: 0.5 });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    group.add(ground);

    const baseMat = new THREE.MeshStandardMaterial({ color: 0xe7ebf0, roughness: 1 });
    const edgeMat = new THREE.LineBasicMaterial({ color: 0xb7c0cc });
    const highlightMat = new THREE.MeshStandardMaterial({ color: 0x1d5fd6, roughness: 0.6 });

    const cols = 7, rows = 7, cell = 1.5;
    let highlightBuilding = null;

    for (let x = 0; x < cols; x++) {
      for (let z = 0; z < rows; z++) {
        if (Math.random() < 0.18) continue; // leave some empty lots
        const isCenter = x === Math.floor(cols / 2) && z === Math.floor(rows / 2);
        const w = cell * (0.55 + Math.random() * 0.3);
        const d = cell * (0.55 + Math.random() * 0.3);
        const h = isCenter ? 5.2 + Math.random() * 0.6 : 0.4 + Math.random() * 1.6;

        const geo = new THREE.BoxGeometry(w, h, d);
        const mesh = new THREE.Mesh(geo, isCenter ? highlightMat : baseMat);
        mesh.position.set(
          (x - cols / 2) * cell + cell / 2,
          h / 2,
          (z - rows / 2) * cell + cell / 2
        );
        group.add(mesh);

        const edges = new THREE.EdgesGeometry(geo);
        const line = new THREE.LineSegments(edges, edgeMat);
        line.position.copy(mesh.position);
        group.add(line);

        if (isCenter) highlightBuilding = mesh;
      }
    }

    const light1 = new THREE.DirectionalLight(0xffffff, 0.9);
    light1.position.set(5, 10, 5);
    scene.add(light1);
    scene.add(new THREE.AmbientLight(0xffffff, 0.65));

    let paused = false;
    let raf = null;

    function resize() {
      const w = container.clientWidth || 1;
      const h = container.clientHeight || 1;
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
    window.addEventListener("resize", resize);
    resize();

    function animate() {
      raf = requestAnimationFrame(animate);
      if (!paused) group.rotation.y += 0.0025;
      renderer.render(scene, camera);
    }
    animate();

    return {
      togglePause() {
        paused = !paused;
        return paused;
      },
      reset() {
        group.rotation.y = 0;
      },
      pauseFor(ms) {
        const wasPaused = paused;
        paused = true;
        setTimeout(() => { paused = wasPaused; }, ms);
      },
    };
  }

  window.UrbanCity = { init: initCity };
})();
