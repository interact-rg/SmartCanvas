import React, { useRef, useEffect } from "react";
import brushImg from "../assets/brush.png";

interface ImagePainterProps {
  filter: string;
}

const ImagePainter: React.FC<ImagePainterProps> = ({ filter }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const width = window.innerWidth;
    const height = window.innerHeight;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    const image = new Image();
    const brush = new Image();
    image.src = "/images/painterly.jpg";
    brush.src = brushImg;

    const maskCanvas = document.createElement("canvas");
    maskCanvas.width = width;
    maskCanvas.height = height;
    const maskCtx = maskCanvas.getContext("2d");

    let t = 0;
    let animationFrame: number;
    let row = 0;
    const spacing = Math.min(height, width) * 0.3;
    const brushSize = Math.min(width, height) * 0.3;
    let previousX = -1;

    const draw = () => {
      const x = (t * 2) % width;
      const yOffset = row * spacing - 50;
      const y = Math.sin(t / 10) * spacing * 0.5 + yOffset;

      if (x < previousX && y > height - 30) {
        cancelAnimationFrame(animationFrame);
        return;
      }

      if (maskCtx) {
        maskCtx.globalAlpha = 0.25;
        maskCtx.drawImage(brush, x - brushSize / 2, y - brushSize / 2, brushSize, brushSize);
      }

      if (!ctx) return;
      ctx.clearRect(0, 0, width, height);
      ctx.drawImage(image, 0, 0, width, height);
      ctx.globalCompositeOperation = "destination-in";
      ctx.drawImage(maskCanvas, 0, 0);
      ctx.globalCompositeOperation = "source-over";

      if (previousX > x) {
        row += 1;
      }
      previousX = x;

      t += 3;
      animationFrame = requestAnimationFrame(draw);
    };

    image.onload = () => {
      brush.onload = () => {
        draw();
      };
    };

    return () => cancelAnimationFrame(animationFrame);
  }, [filter]);

  return (
    <canvas
      ref={canvasRef}
      width={window.innerWidth}
      height={window.innerHeight}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        pointerEvents: "none",
      }}
    />
  );
};

export default ImagePainter;
