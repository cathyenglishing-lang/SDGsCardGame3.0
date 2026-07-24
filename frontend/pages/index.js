import * as THREE from 'three';
import { OrbitControls } from 'https://unpkg.com/three@latest/examples/jsm/controls/OrbitControls.js';

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 10, 15)

const renderer = new THREE.WebGLRenderer({antialias: true});
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild( renderer.domElement );

// Import textures.
// image source: https://www.deviantart.com/kirriaa/art/Free-star-sky-HDRI-spherical-map-719281328

// Import textures.
// image source: https://www.deviantart.com/kirriaa/art/Free-star-sky-HDRI-spherical-map-719281328
const skydomeTexture = new THREE.TextureLoader().load('https://storage.googleapis.com/umas_public_assets/michaelBay/free_star_sky_hdri_spherical_map_by_kirriaa_dbw8p0w%20(1).jpg')
// Apply material on both sides.
const skydomeMaterial = new THREE.MeshBasicMaterial( { map: skydomeTexture, side: THREE.DoubleSide})
const skydomeGeometry = new THREE.SphereGeometry(100,50,50)
const skydome = new THREE.Mesh(skydomeGeometry, skydomeMaterial);
scene.add(skydome);

// Add ambient light.
const addAmbientLight = () => {
	const light = new THREE.AmbientLight(0xffffff, 0.5)
	scene.add(light)
}

// Add point light.
const addPointLight = () => {
	const pointLight = new THREE.PointLight(0xffffff, 1)
	scene.add(pointLight);
	pointLight.position.set(10, 10, -10)
	pointLight.castShadow = true
	// Add helper.
	const lightHelper = new THREE.PointLightHelper(pointLight, 5, 0xffff00)
	// scene.add(lightHelper);
	// Update helper.
	lightHelper.update();
}

// Add directional light.
const addDirectionalLight = () => {
	const directionalLight = new THREE.DirectionalLight(0xffffff, 1)
	directionalLight.position.set(0, 0, 10)
	scene.add(directionalLight);
	directionalLight.castShadow = true
	const d = 10;

	directionalLight.shadow.camera.left = - d;
	directionalLight.shadow.camera.right = d;
	directionalLight.shadow.camera.top = d;
	directionalLight.shadow.camera.bottom = - d;

	// Add helper.
	const lightHelper = new THREE.DirectionalLightHelper(directionalLight, 5, 0xffff00)
	// scene.add(lightHelper);
	// Update position.
	directionalLight.target.position.set(0, 0, 0);
	directionalLight.target.updateMatrixWorld();
	// Update helper.
	lightHelper.update();
}

addPointLight()
addAmbientLight()
addDirectionalLight()

const earthGeometry = new THREE.SphereGeometry(5,600,600)
const earthTexture = new THREE.TextureLoader().load('https://storage.googleapis.com/umas_public_assets/michaelBay/day10/8081_earthmap2k.jpg')
// Grayscale height map.
const displacementTexture = new THREE.TextureLoader().load('https://storage.googleapis.com/umas_public_assets/michaelBay/day10/editedBump.jpg')
const roughtnessTexture = new THREE.TextureLoader().load('https://storage.googleapis.com/umas_public_assets/michaelBay/day10/8081_earthspec2kReversedLighten.png')
const speculatMapTexture = new THREE.TextureLoader().load('https://storage.googleapis.com/umas_public_assets/michaelBay/day10/8081_earthspec2k.jpg')
const bumpTexture = new THREE.TextureLoader().load('https://storage.googleapis.com/umas_public_assets/michaelBay/day10/8081_earthbump2k.jpg')


const earthMaterial = new THREE.MeshStandardMaterial( { 
	map: earthTexture, 
	side: THREE.DoubleSide, 
	roughnessMap:roughtnessTexture,
	roughness:0.9,
	// Apply maps to the material parameters.
	metalnessMap: speculatMapTexture,
	metalness:1,
	displacementMap:displacementTexture,
	displacementScale:0.5,
	bumpMap: bumpTexture,
	bumpScale: 0.1	,
})
const earth = new THREE.Mesh(earthGeometry, earthMaterial);
scene.add(earth);

const cloudGeometry = new THREE.SphereGeometry(5.4,60,60)
// Import texture.
// texture source: http://planetpixelemporium.com/earth8081.html
const cloudTransparency = new THREE.TextureLoader().load('https://storage.googleapis.com/umas_public_assets/michaelBay/day10/8081_earthhiresclouds2K.jpg')
// Apply material settings.
const cloudMaterial = new THREE.MeshStandardMaterial( { 
	transparent: true, 
	opacity: 1,
	alphaMap: cloudTransparency
})
const cloud = new THREE.Mesh(cloudGeometry, cloudMaterial);
scene.add(cloud);


// Initialize controls with the camera and renderer DOM element.
new OrbitControls( camera, renderer.domElement );

const axesHelper = new THREE.AxesHelper( 5 );
scene.add( axesHelper );

function animate() {
	requestAnimationFrame( animate );
	renderer.render( scene, camera );
	earth.rotation.y +=0.005
	cloud.rotation.y +=0.004
  skydome.rotation.y += 0.001

}
animate();
