interface ProgressCircleProps {
    progress: number;
    position: [number, number];
    }

const ProgressCircle: React.FC<ProgressCircleProps> = ({ progress, position }) => {
    const visible = progress > 0 && progress < 1 ? 1 : 0;
    //TODO: Make the bar stick around for a bit when no position or progress?
    if (position[0] === 0 && position[1] === 0) {
        return null;
    }
    return (
        <div id="progress-circle" style={{
            "--right": `${position[0] * 100}%`, 
            "--top": `${position[1] * 100}%`, 
            "--progress": `${progress * 100}%`, 
            "--visible": visible
            } as React.CSSProperties}>
        </div>
    );
}

export default ProgressCircle;