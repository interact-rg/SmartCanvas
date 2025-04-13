import React, { useEffect, useRef } from "react";
import brushImg from "../assets/brush.png";

interface ImagePainterProps {
  canvas: HTMLCanvasElement | null;
  filter: string;
  interrupt: boolean;
  averageTime: number; // Average time spent processing the image in the backend
  onInterrupt: (ack: boolean) => void; // Callback to notify the parent component about the interrupt
}

const ImagePainter: React.FC<ImagePainterProps> = ({ canvas, filter, interrupt, averageTime = 2, onInterrupt }) => {
  //const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animationRef = useRef<number | null>(null); // Use a ref to store the animation frame ID
  const interruptRef = useRef(interrupt); // Use a ref to track the latest interrupt value

  // Update the interrupt ref whenever the interrupt prop changes
  useEffect(() => {
    interruptRef.current = interrupt;
    //console.log("Interrupt updated in ImagePainter:", interrupt);

    // Stop the animation immediately if interrupt is true
    if (interrupt) {
      //console.log("Animation stopped due to interrupt.");
      onInterrupt(true); // Notify the parent component about the interrupt
    }
  }, [interrupt]);

  useEffect(() => {
    //console.log("Average time updated in ImagePainter:", averageTime);
  }, [averageTime]);

  useEffect(() => {

    const width = canvas?.width || 1280;
    const height = canvas?.height || 720;

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
    // const spacing = Math.min(height, width) * 0.5;
    // const brushSize = Math.min(width, height) * 0.3;

    // Dynamically calculate spacing and brush size
    const roundedAverageTime = Math.max(1, Math.floor(averageTime)); // Round the average time to the down nearest integer
    const timeForOneRow = 5; // Estimated time to paint one row, tweak as needed

    let maxRows = 1; // Default to 1 row
    if (roundedAverageTime > timeForOneRow) {
        maxRows = Math.round(roundedAverageTime / timeForOneRow); // Calculate the maximum number of rows based on average time
    }

    const spacing = Math.min(height, width) * (1 / maxRows); // Base spacing based on the maximum number of rows
    const brushSize = Math.min(width, height) * 0.3; // Brush size
    //console.log("Spacing:", spacing, "Brush Size:", brushSize, "Max Rows:", maxRows);

    let previousX = -1;

    const draw = () => {
      if (interruptRef.current) {
        // Interrupt received from the parent component
        if (animationRef.current !== null) {
          //console.log("Animation interrupted.");
          cancelAnimationFrame(animationRef.current);
          animationRef.current = null;
          onInterrupt(true); // Notify the parent component about the interrupt
        }
        return;
      }

      const x = (t * 2) % width;
      const yOffset = row * spacing + spacing * 0.5;
      const y = Math.sin(t / 10) * spacing * 0.4 + yOffset;

      //if (row == 2) {
      if (row >= maxRows) {
        // Animation complete
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
        onInterrupt(true); // Notify the parent component about the interrupt
        //console.log("Ack sent by cleanup function.");
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
