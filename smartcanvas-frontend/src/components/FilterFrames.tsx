import React, { useState, useRef, useEffect } from "react";

interface FilterFramesProps {
  availableFilters: string[];
  chosenFilter: string | "";
}

const FilterFrames: React.FC<FilterFramesProps> = ({
  availableFilters,
  chosenFilter,
}) => {
  // Construct filter paths dynamically using availableFilters
  const filters =
    availableFilters.length !== 0
      ? availableFilters.map((filterName) => `/images/${filterName}.jpg`)
      : ["/images/anime style.jpg"];

  //console.log("Filters: ", availableFilters);
  //console.log( "Chosen filter: " + chosenFilter + ", index: ", availableFilters.indexOf(chosenFilter));

  const [chosenFilterIndex, setChosenFilterIndex] = useState<number>(0); // Max value: filters.length
  const containerRef = useRef<HTMLDivElement>(null);

  // Update chosenFilterIndex when chosenFilter changes
  useEffect(() => {
    const newChosenFilterIndex = availableFilters.indexOf(chosenFilter);
    // Only update if the chosenFilter is found in the availableFilters
    if (newChosenFilterIndex >= 0) {
      setChosenFilterIndex(newChosenFilterIndex);
    }
  }, [chosenFilter, availableFilters]); // Re-run this effect when chosenFilter or availableFilters change

  // This function will center the selected filter and make sure it's fully visible
  const scrollToSelectedFilter = (index: number) => {
    if (containerRef.current) {
      const container = containerRef.current;
      const selectedFilter = container.children[index] as HTMLElement;

      // Calculate the left offset of the selected filter
      const filterOffset = selectedFilter.offsetLeft;
      const containerWidth = container.offsetWidth;

      // Make sure the filter image is fully visible by adjusting the scroll position
      const scrollPosition =
        filterOffset - containerWidth / 2 + selectedFilter.offsetWidth / 2;

      // Scroll to the calculated position with smooth behavior
      container.scrollTo({
        left: scrollPosition,
        behavior: "smooth",
      });
    }
  };

  // Automatically center the selected filter when the component is mounted or the index changes
  useEffect(() => {
    scrollToSelectedFilter(chosenFilterIndex);
  }, [chosenFilterIndex]);

  return (
    <div
      ref={containerRef}
      style={{
        position: "absolute",
        bottom: "10px", // Adjust this to move the box higher or lower
        left: "50%",
        transform: "translateX(-50%)",
        display: "flex",
        overflowX: "hidden", // Hide the scrollbar
        paddingBottom: "5px", // Add more padding at the bottom
        width: "90%", // Increase the width of the box
        maxWidth: "1000px",
        scrollBehavior: "smooth", // Enable smooth scrolling
      }}
    >
      {filters.map((filter, index) => (
        <img
          key={index}
          src={filter}
          alt={`frame-${index}`}
          style={{
            width: "100px", // Width of images
            height: "100px",
            margin: "0 10px", // Margin between images
            borderRadius: "10px", // Make corners rounder
            border: `solid ${
              chosenFilterIndex === index ? "#ff6347 4px" : "#ccc 2px"
            }`, // Apply bigger border if selected
            cursor: "pointer",
            boxSizing: "border-box",
            transition: "border 0.3s ease", // Smooth transition for border change
          }}
        />
      ))}
    </div>
  );
};

export default FilterFrames;
