import visual from "../assets/consent_visual.gif";

const ConsentForm = () => {

    return (
        <div
            style={{
                position: "fixed",
                top: 0,
                left: 0,
                width: "100%",
                height: "100%",
                backgroundColor: "rgba(0,0,0,0.85)",
                color: "white",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                zIndex: 99999,
                textAlign: "center",
                padding: "20px",
                pointerEvents: "auto",
                fontSize: "1.5rem",
                boxSizing: "border-box",     // include padding in width
                overflowX: "hidden"          // extra safety to prevent horizontal scroll
            }}
        >
            <img src={visual} alt="Description of service data flow." />
            <button
                style={{ fontSize: "2rem", margin: "10px" }}>
                By giving 👍 you accept that your image will be processed.
            </button>
        </div>
    );
};

export default ConsentForm;