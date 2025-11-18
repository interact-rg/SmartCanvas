import React, { useState, useRef, useEffect } from "react";

interface FilterFramesProps {
  availableFilters: string[];
  chosenFilter: string | "";
}

type FilterFrame = {
  image: string;
  key: number;
};

const FilterFrames: React.FC<FilterFramesProps> = ({
  availableFilters,
  chosenFilter,
}) => {
  // Construct filter paths dynamically using availableFilters
  const filters: string[] =
    availableFilters.length !== 0
      ? availableFilters.map((filterName) => `/images/${filterName}.jpg`)
      : ["/images/anime style.jpg"]; // Default filter if availableFilters is empty

  const [chosenFilterIndex, setChosenFilterIndex] = useState<number>(0); // Max value: filters.length
  const containerRef = useRef<HTMLDivElement>(null);
  const [paddedList, setPaddedList] = useState<FilterFrame[]>([]);
  const MAX_FILTERS = 5; // number of filters to display on both sides

  // Update chosenFilterIndex when chosenFilter changes
  useEffect(() => {
    const filterIndex = availableFilters.indexOf(chosenFilter);
    // Only update if the chosenFilter is found in the availableFilters
    if (filterIndex >= 0) {
      setChosenFilterIndex(filterIndex);
      let list: FilterFrame[] = [];

      for (let i = -MAX_FILTERS; i <= MAX_FILTERS; i++) {
        list.push({
          image: filters[(filterIndex + i + filters.length) % filters.length],
          key: filterIndex + i,
        });
      }
      setPaddedList(list);
    }
  }, [chosenFilter, availableFilters]); // Re-run this effect when chosenFilter or availableFilters change

  return (
    <div id="filter-carousel" ref={containerRef}>
      {/* TODO: carousel "snaps" when looping over */}
      {paddedList.map((filter) => (
        <img
          key={filter.key}
          src={filter.image}
          className={filter.key === chosenFilterIndex ? "selected" : ""}
        />
      ))}
    </div>
  );
};

export default FilterFrames;
