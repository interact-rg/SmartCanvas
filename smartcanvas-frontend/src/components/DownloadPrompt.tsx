import React, { useEffect, useRef } from 'react';

interface DownloadPromptProps {
    image: string | null;
    downloadQr: string | null;
};

const DownloadPrompt: React.FC<DownloadPromptProps> = ({ image, downloadQr }) => {
    return (
        <div id="qr-popup" className={`${image && downloadQr ? "active" : "dismissed"}`}>
            <div id="qr-wrapper">
                <img src={`data:image/jpeg;base64,${image}`} alt="" id="download-image"/>
                {/* Get bespoke icon? */}
                <span>⬇️</span>
                <img src={`data:image/jpeg;base64,${downloadQr}`} alt="" id="qr-code"/>
            </div>
        </div>
    );
};

export default DownloadPrompt;