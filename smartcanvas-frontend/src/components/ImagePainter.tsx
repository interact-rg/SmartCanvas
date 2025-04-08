import React, { useEffect, useRef } from "react";
import brushImg from "../assets/brush.png";

interface ImagePainterProps {
  canvas: HTMLCanvasElement | null;
  filter: string;
  interrupt: boolean;
}

const ImagePainter: React.FC<ImagePainterProps> = ({ canvas, filter, interrupt}) => {
  //const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animationRef = useRef<number | null>(null); // Use a ref to store the animation frame ID
  const interruptRef = useRef(interrupt); // Use a ref to track the latest interrupt value

  // Update the interrupt ref whenever the interrupt prop changes
  useEffect(() => {
    interruptRef.current = interrupt;
    console.log("Interrupt updated in ImagePainter:", interrupt);

    // Stop the animation immediately if interrupt is true
    if (interrupt && animationRef.current !== null) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
      //console.log("Animation stopped due to interrupt.");
    }
  }, [interrupt]);

  useEffect(() => {
    // const width = window.innerWidth;
    // const height = window.innerHeight;
    const width = canvas?.width || 1280;
    const height = canvas?.height || 720;
    //const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    const image = new Image();
    const brush = new Image();

    // Get the image from currently selected filter
    image.src = `/images/${filter}.jpg`;
    brush.src = brushImg;

    const maskCanvas = document.createElement("canvas");
    maskCanvas.width = width;
    maskCanvas.height = height;
    const maskCtx = maskCanvas.getContext("2d");

    let t = 0;
    let animationFrame: number;
    let row = 0;
    const spacing = Math.min(height, width) * 0.5;
    const brushSize = Math.min(width, height) * 0.3;
    let previousX = -1;

    const draw = () => {
      if (interruptRef.current) {
        //console.log("Interrupting animation...");
        if (animationRef.current !== null) {
          cancelAnimationFrame(animationRef.current); // Stop the animation if interrupt is true
          animationRef.current = null;
        }
        return;
      }

      const x = (t * 2) % width;
      const yOffset = row * spacing + spacing * 0.5;
      const y = Math.sin(t / 10) * spacing * 0.4 + yOffset;

      if (row == 2) {
        cancelAnimationFrame(animationFrame);
        return;
      }

      if (maskCtx) {
        maskCtx.globalAlpha = 0.25;
        maskCtx.drawImage(brush, x - brushSize / 2, y - brushSize / 2, brushSize, brushSize);
      }

      if (!ctx) return;
      // Draw the filtered image with the mask
      ctx.drawImage(image, 0, 0, width, height);
      ctx.globalCompositeOperation = "destination-in";
      ctx.drawImage(maskCanvas, 0, 0);
      ctx.globalCompositeOperation = "source-over";

      if (previousX > x) {
        row += 1;
      }
      previousX = x;

      t += 2;

      animationFrame = requestAnimationFrame(draw);
    };

    image.onload = () => {
      brush.onload = () => {
        draw();
      };
    };

    return () => {
      // Cleanup animation on unmount
      //console.log("ImagePainter unmounted, cleaning up animation.");
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }
    };
  }, [filter, canvas]);


  return null;//(
  //   <canvas
  //     ref={canvasRef}
  //     width={window.innerWidth}
  //     height={window.innerHeight}
  //     style={{
  //       position: "absolute",
  //       top: 0,
  //       left: 0,
  //       width: "100vw",
  //       height: "100vh",
  //       pointerEvents: "none",
  //     }}
  //   />
  // );
};

export default ImagePainter;
