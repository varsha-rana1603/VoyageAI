import { QuizQuestion } from "./types";

export const quizQuestions: QuizQuestion[] = [
  {
    id: "travel_style",
    question: "What kind of trip are you looking for?",
    options: [
      "Adventure",
      "Relaxation",
      "Culture",
      "Luxury",
      "Offbeat"
    ]
  },
  {
    id: "budget",
    question: "What's your budget?",
    options: [
      "Budget",
      "Medium",
      "Luxury"
    ]
  },
  {
    id: "crowd_tolerance",
    question: "How do you feel about crowds?",
    options: [
      "Love Crowds",
      "Some Are Okay",
      "Avoid Crowds"
    ]
  },
  {
    id: "terrain",
    question: "Which landscape excites you the most?",
    options: [
      "Mountains",
      "Beach",
      "Forest",
      "City",
      "Desert"
    ]
  }
];