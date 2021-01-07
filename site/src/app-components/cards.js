import React from "react";

import book from "../img/book.jpg";
import books from "../img/books.jpg";
import chart from "../img/chart.jpg";

const Card = ({ title, text, img, imgAlt, href }) => {
  return (
    <a href={href}>
      <div className="max-w-xs rounded overflow-hidden shadow-lg hover:shadow-2xl">
        <img className="w-full" src={img} alt={imgAlt} />
        <div className="px-6 py-4">
          <div className="font-bold text-xl mb-2">{title}</div>
          <p className="text-gray-700 text-base">{text}</p>
        </div>
        <div className="px-6 py-4"></div>
      </div>
    </a>
  );
};

export const CardExplore = () =>
  Card({
    title: "Explore the Data",
    text: "Browse the map, and visualize the data for powerful data insights",
    img: chart,
    imgAlt: "Computer screen showing graph",
    href: "/explorer",
  });

export const CardCatalog = () =>
  Card({
    title: "Search the Catalog",
    text: "Learn what's available for your study or realtime model",
    img: books,
    imgAlt: "stack of books",
    href: "/catalog",
  });

export const CardDocs = () =>
  Card({
    title: "Documentation",
    text: "How it works and how it's built. User Guide and API Docs.",
    img: book,
    imgAlt: "open book on a table",
    href: "/#docs",
  });
