class FoundryHUD {
    constructor() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.init();
        this.createParticles();
        this.animate();
        this.bindEvents();
    }

    init() {
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        document.getElementById('canvas-container').appendChild(this.renderer.domElement);
        this.camera.position.z = 2;
    }

    createParticles() {
        const geometry = new THREE.BufferGeometry();
        const vertices = [];
        for (let i = 0; i < 2000; i++) {
            vertices.push(
                THREE.MathUtils.randFloatSpread(5),
                THREE.MathUtils.randFloatSpread(5),
                THREE.MathUtils.randFloatSpread(5)
            );
        }
        geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
        const material = new THREE.PointsMaterial({ color: 0xf0c674, size: 0.004, transparent: true, opacity: 0.25 });
        this.particles = new THREE.Points(geometry, material);
        this.scene.add(this.particles);
    }

    bindEvents() {
        window.addEventListener('resize', () => {
            this.camera.aspect = window.innerWidth / window.innerHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(window.innerWidth, window.innerHeight);
        });

        const forgeBtn = document.getElementById('btn-forge');
        forgeBtn.addEventListener('click', () => this.startForge());
    }

    async startForge() {
        const prompt = document.getElementById('foundry-prompt').value.trim();
        if (!prompt) return;

        const status = document.getElementById('gen-status');
        const progress = document.getElementById('progress-fill');
        const statusText = document.getElementById('status-text');
        
        status.style.display = 'block';
        document.getElementById('btn-forge').disabled = true;

        const steps = [
            { t: 0, msg: "HEURISTIC_ANALYSIS_IN_PROGRESS..." },
            { t: 30, msg: "FORGING_LANDING_PAGE_STENCILS..." },
            { t: 60, msg: "INJECTING_STRIPE_REVENUE_HOOKS..." },
            { t: 90, msg: "CRYPTO_VAULT_ENCRYPTION..." }
        ];

        for (let step of steps) {
            statusText.innerText = step.msg;
            progress.style.width = `${step.t}%`;
            await new Promise(r => setTimeout(r, 1500));
        }

        try {
            const res = await fetch('/api/forge', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt })
            });
            const data = await res.json();
            
            progress.style.width = '100%';
            statusText.innerText = "SUCCESS // SAAS_LIVE";
            this.addToVault(data);
        } catch (err) {
            statusText.innerText = "ERROR // CORE_OVERHEAT";
            console.error(err);
        } finally {
            document.getElementById('btn-forge').disabled = false;
        }
    }

    addToVault(data) {
        const vault = document.getElementById('vault-grid');
        const item = document.createElement('div');
        item.className = 'vault-item';
        item.innerHTML = `
            <span class="item-name">${data.name.toUpperCase()}</span>
            <a href="${data.url}" class="btn-view" target="_blank">View Site</a>
        `;
        vault.prepend(item);
        
        const currentCount = parseInt(document.querySelector('.vault-status').innerText.match(/\d+/)[0]);
        document.querySelector('.vault-status').innerText = `VAULT_ENCRYPTED // ${currentCount + 1} PROJECTS`;
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        this.particles.rotation.y += 0.0003;
        this.particles.rotation.x += 0.0001;
        this.renderer.render(this.scene, this.camera);
    }
}

window.onload = () => new FoundryHUD();
