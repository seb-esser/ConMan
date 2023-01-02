<template>
  <div>
    <div>
      <input type="file" id="file-input"/>
    </div>

    <p id="properties-text">
      ID:
      {{ entityData }}
    </p>
    <canvas id="model"/>
  </div>
</template>

<script lang="js">
import IfcManager from '../IFC/IfcManager'
import {Raycaster, Vector2} from 'three'

export default {
  name: 'ModelViewer',
  props: ['token', 'projectId', 'discipline'],

  data() {
    return {
      entityData: '',
    }
  },

  methods: {
    onLoaded: function () {
      this.addPicking()
      this.setupPick(this)
    },
    addPicking: function () {
      this.raycaster = new Raycaster()
      this.raycaster.firstHitOnly = true
      this.mouse = new Vector2()
    },
    cast: function (event) {
      this.bounds = this.threeCanvas.getBoundingClientRect()
      this.x1 = event.clientX - this.bounds.left
      this.x2 = this.bounds.right - this.bounds.left
      this.mouse.x = (this.x1 / this.x2) * 2 - 1
      this.y1 = event.clientY - this.bounds.top
      this.y2 = this.bounds.bottom - this.bounds.top
      this.mouse.y = -(this.y1 / this.y2) * 2 + 1
      this.raycaster.setFromCamera(
          this.mouse,
          this.IFCManager.scene.camera
      )
      return this.raycaster.intersectObjects(this.IFCManager.scene.ifcModels)
    },

    pick: function (event) {
      this.found = this.cast(event)[0]
      if (this.found) {
        this.index = this.found.faceIndex
        this.geometry = this.found.object.geometry
        this.id = this.IFCManager.scene.ifcModel.getExpressId(
            this.geometry,
            this.index
        )
        this.entityData = this.id
      }
    },
    setupPick: function (component) {
      component.threeCanvas = document.getElementById('model')
      component.threeCanvas.ondblclick = component.pick
    },
  },
  mounted() {
    const self = this
    this.IFCManager = new IfcManager('model')

    let input = document.getElementById('file-input')
    input.addEventListener(
        'change',
        async function (changed) {
          let file = changed.target.files[0]
          let ifcURL = URL.createObjectURL(file)
          self.IFCManager.scene.ifcModel = await self.IFCManager.ifcLoader.loadAsync(ifcURL);
          self.IFCManager.scene.add(self.IFCManager.scene.ifcModel.mesh)

          self.onLoaded()
        },
        false
    )
  },
}
</script>

<style scoped>
#model {
  left: 0%;
  top: 0%;
  width: 90% !important;
  height: 90% !important;
}

#file-input {
  position: absolute;
  left: 0%;
  top: 0%;
  z-index: 100;
}

#properties-text {
  position: absolute;
  left: 0%;
  bottom: 0%;
  z-index: 100;
}
</style>