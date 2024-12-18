"use client"

import { useEffect, useRef, useState } from "react"

const Home = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const [gameInfo, setGameInfo] = useState({
    timeElapsed: 0,
    trainCount1: 0,
    trainCount2: 0,
  })

  const gameState = useRef({
    ball: { x: 0, y: 0 },
    paddles: { player1: 0, player2: 0 },
  })

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d")

    wsRef.current = new WebSocket("ws://localhost:8001/ws")
    wsRef.current.binaryType = "arraybuffer"

    wsRef.current.onmessage = (event) => {
      const buffer = new DataView(event.data)

      const ballX = buffer.getUint16(0, true)
      const ballY = buffer.getUint16(2, true)
      const paddle1Y = buffer.getUint16(4, true)
      const paddle2Y = buffer.getUint16(6, true)
      const timeElapsed = buffer.getUint32(8, true)
      const trainCount1 = buffer.getUint16(12, true)
      const trainCount2 = buffer.getUint16(14, true)

      gameState.current.ball.x = ballX
      gameState.current.ball.y = ballY
      gameState.current.paddles.player1 = paddle1Y
      gameState.current.paddles.player2 = paddle2Y

      setGameInfo({ timeElapsed, trainCount1, trainCount2 })

      draw()
    }

    const draw = () => {
      if (!ctx) return

      ctx.clearRect(0, 0, canvas!.width, canvas!.height)

      ctx.beginPath()
      ctx.arc(gameState.current.ball.x, gameState.current.ball.y, 10, 0, Math.PI * 2)
      ctx.fillStyle = "white"
      ctx.fill()
      ctx.closePath()

      ctx.fillStyle = "white"
      ctx.fillRect(20, gameState.current.paddles.player1, 10, 100)
      ctx.fillRect(570, gameState.current.paddles.player2, 10, 100)
    }

    const handleKeyDown = (e: KeyboardEvent) => {
      if (!wsRef.current) return

      const buffer = new ArrayBuffer(1)
      const view = new DataView(buffer)
      if (e.key === "ArrowUp") view.setUint8(0, 1)
      if (e.key === "ArrowDown") view.setUint8(0, 2)

      wsRef.current.send(buffer)
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => {
      window.removeEventListener("keydown", handleKeyDown)
      wsRef.current?.close()
    }
  }, [])

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-900 text-white">
      <h1 className="text-3xl font-bold mb-6">AI Pong Game</h1>
      <div className="flex gap-8 items-start">
        <canvas ref={canvasRef} width={600} height={400} className="border-4 border-white" />

        <div className="flex flex-col gap-4">
          <div className="p-4 bg-gray-800 rounded shadow-lg">
            <h2 className="text-lg font-semibold">Game Info</h2>
            <p className="text-sm">Time Elapsed: <span className="font-bold">{gameInfo.timeElapsed}s</span></p>
          </div>
          <div className="p-4 bg-gray-800 rounded shadow-lg">
            <h2 className="text-lg font-semibold">Training Info</h2>
            <p className="text-sm">Player 1 Trains: <span className="font-bold">{gameInfo.trainCount1}</span></p>
            <p className="text-sm">Player 2 Trains: <span className="font-bold">{gameInfo.trainCount2}</span></p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
