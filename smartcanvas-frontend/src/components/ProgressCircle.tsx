interface ProgressCircleProps {
  progress: number;
  position: [number, number];
}

const ProgressCircle: React.FC<ProgressCircleProps> = ({
  progress,
  position,
}) => {
  const visible = progress > 0 && progress < 1 ? 1 : 0;
  //TODO: Make the bar stick around for a bit when no position or progress?
  if (position[0] === 0 && position[1] === 0) {
    return null;
  }

  const strokeDasharray = 565.48;
  const strokeDashoffset = strokeDasharray * ((100 - progress * 100) / 100); // Formula for the progress on circle
  const progressColor = `rgb(${140 + 120 * progress}, ${
    255 - 90 * progress
  }, 0)`;
  return (
    <svg
      width="200"
      height="200"
      viewBox="-25 -25 250 250"
      version="1.1"
      xmlns="http://www.w3.org/2000/svg"
      style={
        {
          transform: "rotate(-90deg)",
          "--right": `${position[0] * 100}%`,
          "--top": `${position[1] * 100}%`,
          "--visible": visible,
        } as React.CSSProperties
      }
      id="progress-circle"
    >
      <circle
        r="90"
        cx="100"
        cy="100"
        fill="transparent"
        stroke="#e0e0e0"
        strokeWidth="16px"
      ></circle>
      <circle
        r="90"
        cx="100"
        cy="100"
        stroke={progressColor}
        strokeWidth="16px"
        strokeLinecap="round"
        strokeDashoffset={strokeDashoffset}
        fill="transparent"
        strokeDasharray="565.48px"
      ></circle>
    </svg>
  );
};

export default ProgressCircle;
