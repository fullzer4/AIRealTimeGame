<template>
  <div>
    <h2>Estado do Jogo</h2>
    <canvas ref="canvas" :width="width" :height="height"></canvas>
    <div v-if="!connected">Conectando ao servidor...</div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, onBeforeUnmount, watch } from 'vue'

export default defineComponent({
  name: 'GameGrid',
  props: {
    width: {
      type: Number,
      default: 500
    },
    height: {
      type: Number,
      default: 500
    }
  },
  setup(props) {
    const grid = ref<number[][]>([])
    const connected = ref(false)
    const socket: { current: WebSocket|null } = { current: null }
    const canvas = ref<HTMLCanvasElement|null>(null)
    let ctx: CanvasRenderingContext2D|null = null

    const cellSize = 2 // Ajuste conforme necessário. Aqui cada célula será 2x2 pixels.
    // Isso resultará em uma imagem de 1000x1000px para 500x500 células.
    // Se quiser manter 500x500 pixels exatamente, use cellSize = 1.

    onMounted(() => {
      if (canvas.value) {
        ctx = canvas.value.getContext('2d')
      }

      socket.current = new WebSocket('ws://localhost:8000/ws');

      socket.current.onopen = () => {
        connected.value = true
      };

      socket.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.grid && ctx) {
          grid.value = data.grid
          drawGrid()
        }
      };

      socket.current.onerror = (error) => {
        console.error('Erro no WebSocket:', error);
      };

      socket.current.onclose = () => {
        console.warn('WebSocket fechado');
        connected.value = false
      };
    });

    onBeforeUnmount(() => {
      if (socket.current) {
        socket.current.close();
      }
    });

    function drawGrid() {
      if (!ctx || grid.value.length === 0) return;
      const g = grid.value
      const h = g.length
      const w = g[0].length

      const imageData = ctx.createImageData(w * cellSize, h * cellSize);
      const data = imageData.data;

      for (let r = 0; r < h; r++) {
        for (let c = 0; c < w; c++) {
          let color;
          const cell = g[r][c]
          if (cell === 1) {
            color = [0, 0, 255]
          } else if (cell === 2) {
            color = [255, 0, 0]
          } else {
            color = [200, 200, 200]
          }

          for (let dy = 0; dy < cellSize; dy++) {
            for (let dx = 0; dx < cellSize; dx++) {
              const x = c * cellSize + dx
              const y = r * cellSize + dy
              const index = (y * w * cellSize + x) * 4
              data[index] = color[0]
              data[index+1] = color[1]
              data[index+2] = color[2]
              data[index+3] = 255
            }
          }
        }
      }

      ctx.putImageData(imageData, 0, 0);
    }

    return {
      connected,
      canvas
    }
  }
})
</script>

<style scoped>
canvas {
  border: 1px solid #000;
}
</style>
