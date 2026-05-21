const groups = [
  "City node",
  "Data hub",
  "Threat relay",
  "Signal mesh",
  "Research archive",
  "Infrastructure"
];

function createNodes(count) {
  return Array.from({ length: count }, (_, index) => {
    const band = index / count;
    const theta = index * 2.399963229728653;
    const z = 1 - band * 2;
    const radius = Math.sqrt(1 - z * z);
    const cluster = index % groups.length;

    return {
      id: index,
      label: `${groups[cluster]} ${String(index + 1).padStart(3, "0")}`,
      group: groups[cluster],
      theta,
      x: Math.cos(theta) * radius,
      y: Math.sin(theta) * radius,
      z,
      phase: index * 0.37,
      size: 1.4 + (index % 7) * 0.35,
      pulse: 0.45 + (index % 11) * 0.04
    };
  });
}

function createLinks(nodes) {
  const links = [];

  nodes.forEach((node, index) => {
    const candidates = nodes
      .map((other, otherIndex) => {
        if (otherIndex === index) return null;
        const dx = node.x - other.x;
        const dy = node.y - other.y;
        const dz = node.z - other.z;
        return { source: index, target: otherIndex, distance: dx * dx + dy * dy + dz * dz };
      })
      .filter(Boolean)
      .sort((a, b) => a.distance - b.distance)
      .slice(0, index % 4 === 0 ? 3 : 2);

    candidates.forEach((candidate) => {
      const key = candidate.source < candidate.target
        ? `${candidate.source}-${candidate.target}`
        : `${candidate.target}-${candidate.source}`;

      if (!links.some((link) => link.key === key)) {
        links.push({ ...candidate, key, particle: (index % 17) / 17 });
      }
    });
  });

  return links;
}

function projectNode(node, width, height, time, pointer) {
  const sway = Math.sin(time * 0.55 + node.phase) * 0.035;
  const breathe = Math.cos(time * 0.42 + node.phase) * 0.025;
  const rotationY = time * 0.055 + pointer.x * 0.22;
  const rotationX = -0.22 + pointer.y * 0.16;
  const x = node.x + sway;
  const y = node.y + breathe;
  const z = node.z;
  const cosY = Math.cos(rotationY);
  const sinY = Math.sin(rotationY);
  const rotatedX = x * cosY - z * sinY;
  const rotatedZ = x * sinY + z * cosY;
  const cosX = Math.cos(rotationX);
  const sinX = Math.sin(rotationX);
  const rotatedY = y * cosX - rotatedZ * sinX;
  const finalZ = y * sinX + rotatedZ * cosX;
  const depth = 1.8 + finalZ * 0.38;
  const isCompact = width < 700;
  const centerX = width / 2;
  const centerY = isCompact ? height * 0.52 : height * 0.5;
  const scale = Math.min(width, height) * (isCompact ? 0.7 : 0.72);

  return {
    x: centerX + (rotatedX / depth) * scale,
    y: centerY + (rotatedY / depth) * scale,
    z: finalZ,
    alpha: 0.18 + (finalZ + 1) * 0.32,
    size: node.size * (1.1 + finalZ * 0.2),
    node
  };
}

function initKnowledgeGraph(canvas) {
  const ctx = canvas.getContext("2d", { alpha: true });
  const wrapper = canvas.closest(".knowledge-graph");
  const tooltip = wrapper?.querySelector("[data-graph-tooltip]");
  const tooltipGroup = wrapper?.querySelector("[data-tooltip-group]");
  const tooltipTitle = wrapper?.querySelector("[data-tooltip-title]");
  const tooltipSignal = wrapper?.querySelector("[data-tooltip-signal]");
  const nodes = createNodes(132);
  const links = createLinks(nodes);
  const pointer = { x: 0, y: 0 };
  let projected = [];
  let hoveredId = null;
  let width = 0;
  let height = 0;
  let frameId = 0;

  const resize = () => {
    const rect = canvas.getBoundingClientRect();
    const ratio = Math.min(window.devicePixelRatio || 1, 1.35);
    canvas.width = Math.max(1, Math.floor(rect.width * ratio));
    canvas.height = Math.max(1, Math.floor(rect.height * ratio));
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    width = rect.width;
    height = rect.height;
  };

  const draw = (timestamp) => {
    const time = timestamp * 0.001;
    ctx.clearRect(0, 0, width, height);
    projected = nodes.map((node) => projectNode(node, width, height, time, pointer));

    const gradient = ctx.createRadialGradient(width / 2, height / 2, 20, width / 2, height / 2, Math.min(width, height) * 0.45);
    gradient.addColorStop(0, "rgba(255,255,255,0.045)");
    gradient.addColorStop(0.65, "rgba(255,255,255,0.012)");
    gradient.addColorStop(1, "rgba(255,255,255,0)");
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.arc(width / 2, height / 2, Math.min(width, height) * 0.42, 0, Math.PI * 2);
    ctx.fill();

    links.forEach((link, index) => {
      const source = projected[link.source];
      const target = projected[link.target];
      const depthAlpha = Math.max(0.05, Math.min(source.alpha, target.alpha));
      const pulse = 0.35 + Math.sin(time * 1.8 + index) * 0.18;
      ctx.strokeStyle = `rgba(255,255,255,${depthAlpha * pulse})`;
      ctx.lineWidth = 0.55;
      ctx.beginPath();
      ctx.moveTo(source.x, source.y);
      ctx.lineTo(target.x, target.y);
      ctx.stroke();

      if (index % 3 === 0) {
        const flow = (time * 0.16 + link.particle) % 1;
        const x = source.x + (target.x - source.x) * flow;
        const y = source.y + (target.y - source.y) * flow;
        ctx.fillStyle = `rgba(255,255,255,${depthAlpha * 0.75})`;
        ctx.beginPath();
        ctx.arc(x, y, 1.2, 0, Math.PI * 2);
        ctx.fill();
      }
    });

    projected.forEach((point) => {
      const pulse = 0.65 + Math.sin(time * 2.2 + point.node.phase) * point.node.pulse;
      const alpha = Math.max(0.16, Math.min(0.92, point.alpha * pulse));
      ctx.shadowColor = "rgba(255,255,255,0.7)";
      ctx.shadowBlur = 7;
      ctx.fillStyle = `rgba(255,255,255,${alpha})`;
      ctx.beginPath();
      ctx.arc(point.x, point.y, point.size, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;
    });

    frameId = window.requestAnimationFrame(draw);
  };

  const onPointerMove = (event) => {
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    pointer.x = (x / rect.width - 0.5) * 2;
    pointer.y = (y / rect.height - 0.5) * 2;

    const hovered = projected
      .map((point) => {
        const dx = point.x - x;
        const dy = point.y - y;
        return { point, distance: Math.sqrt(dx * dx + dy * dy) };
      })
      .filter(({ distance }) => distance < 13)
      .sort((a, b) => a.distance - b.distance)[0];

    const nextId = hovered?.point.node.id ?? null;
    if (nextId === hoveredId) return;
    hoveredId = nextId;

    if (hovered && tooltip) {
      tooltip.hidden = false;
      tooltip.style.left = `${x + 18}px`;
      tooltip.style.top = `${y + 18}px`;
      tooltipGroup.textContent = hovered.point.node.group;
      tooltipTitle.textContent = hovered.point.node.label;
      tooltipSignal.textContent = `${Math.round((hovered.point.alpha + 0.2) * 82)}% linked`;
    } else if (tooltip) {
      tooltip.hidden = true;
    }
  };

  const onPointerLeave = () => {
    pointer.x = 0;
    pointer.y = 0;
    hoveredId = null;
    if (tooltip) tooltip.hidden = true;
  };

  const observer = new ResizeObserver(resize);
  observer.observe(canvas);
  canvas.addEventListener("pointermove", onPointerMove);
  canvas.addEventListener("pointerleave", onPointerLeave);
  resize();
  frameId = window.requestAnimationFrame(draw);

  return () => {
    window.cancelAnimationFrame(frameId);
    observer.disconnect();
    canvas.removeEventListener("pointermove", onPointerMove);
    canvas.removeEventListener("pointerleave", onPointerLeave);
  };
}

document.querySelectorAll("[data-graph-canvas]").forEach(initKnowledgeGraph);
