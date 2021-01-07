import React from "react";

import "./loader.css";

export default function Loader({ opt, color }) {
  const customStyle = {};
  if (color) customStyle.backgroundColor = color;
  if (opt === "dissolve-cube") {
    return (
      <div className="dissolve-cube-grid">
        <div className="dissolve-cube dissolve-cube1" style={customStyle}></div>
        <div className="dissolve-cube dissolve-cube2" style={customStyle}></div>
        <div className="dissolve-cube dissolve-cube3" style={customStyle}></div>
        <div className="dissolve-cube dissolve-cube4" style={customStyle}></div>
        <div className="dissolve-cube dissolve-cube5" style={customStyle}></div>
        <div className="dissolve-cube dissolve-cube6" style={customStyle}></div>
        <div className="dissolve-cube dissolve-cube7" style={customStyle}></div>
        <div className="dissolve-cube dissolve-cube8" style={customStyle}></div>
        <div className="dissolve-cube dissolve-cube9" style={customStyle}></div>
      </div>
    );
  }
  if (opt === "spin-cubes") {
    return (
      <div className="spin-cubes">
        <div className="cube1" style={customStyle}></div>
        <div className="cube2" style={customStyle}></div>
      </div>
    );
  } else if (opt === "marching-bars") {
    return (
      <div className="marching-bars">
        <div className="rect1" style={customStyle}></div>
        <div className="rect2" style={customStyle}></div>
        <div className="rect3" style={customStyle}></div>
        <div className="rect4" style={customStyle}></div>
        <div className="rect5" style={customStyle}></div>
      </div>
    );
  } else {
    return (
      <div className="sk-folding-cube">
        <div className="sk-cube1 sk-cube" style={customStyle}></div>
        <div className="sk-cube2 sk-cube" style={customStyle}></div>
        <div className="sk-cube4 sk-cube" style={customStyle}></div>
        <div className="sk-cube3 sk-cube" style={customStyle}></div>
      </div>
    );
  }
}
