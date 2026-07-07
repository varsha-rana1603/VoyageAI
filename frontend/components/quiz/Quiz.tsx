"use client";

import { useEffect, useState } from "react";
import { AnimatePresence } from "framer-motion";

import Question from "./Question";
import ProgressBar from "./ProgressBar";
import FreeText from "./FreeText";

import ThinkingScreen, {
  destinationPipeline,
} from "../thinking/ThinkingScreen";

import ResultsPage from "../recommendations/ResultsPage";
import { quizQuestions } from "./quizData";


export default function Quiz() {

  const [step, setStep] = useState(0);


  const [stage, setStage] = useState<
    "quiz" | "freeText" | "thinking" | "results"
  >("quiz");


  const [answers, setAnswers] = useState<Record<string, string>>({});

  const [freeText, setFreeText] = useState("");


  const [recommendations, setRecommendations] = useState<any[]>([]);

  const [fetchError, setFetchError] = useState<string | null>(null);


  const [animationDone, setAnimationDone] = useState(false);

  const [fetchDone, setFetchDone] = useState(false);



  function handleAnswer(answer: string) {

    const updated = {
      ...answers,
      [quizQuestions[step].id]: answer,
    };


    setAnswers(updated);



    if (step === quizQuestions.length - 1) {

      setTimeout(() => {
        setStage("freeText");
      }, 300);

      return;
    }



    setTimeout(() => {
      setStep(step + 1);
    }, 300);

  }





  /*
    Fetch recommendations while ThinkingScreen is running
  */

  useEffect(() => {

    if (stage !== "thinking") return;


    setAnimationDone(false);
    setFetchDone(false);
    setFetchError(null);


    let cancelled = false;



    async function fetchRecommendations() {

      try {


        const res = await fetch(
          "http://127.0.0.1:8001/recommend",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },

            body: JSON.stringify({

              travel_style: answers.travel_style,

              budget: answers.budget,

              crowd_tolerance: answers.crowd_tolerance,

              terrain: answers.terrain,

              free_text: freeText,

            }),
          }
        );



        const rawText = await res.text();



        if (!res.ok) {

          throw new Error(
            `Server Error ${res.status}: ${rawText}`
          );

        }



        const data = JSON.parse(rawText);



        if (!cancelled) {

          setRecommendations(
            data.recommendations || data
          );

        }



      } catch (err: any) {


        console.error(
          "FETCH ERROR:",
          err
        );


        if (!cancelled) {

          setFetchError(
            err.message ||
            "Backend connection failed"
          );

        }


      }
      finally {

        if (!cancelled) {

          setFetchDone(true);

        }

      }


    }



    fetchRecommendations();



    return () => {

      cancelled = true;

    };


  }, [
    stage,
    answers,
    freeText
  ]);






  /*
    Move to results only when:
    1. AI animation completed
    2. Backend returned results
  */

  useEffect(() => {


    if (
      stage === "thinking" &&
      animationDone &&
      fetchDone
    ) {

      setStage("results");

    }


  }, [
    stage,
    animationDone,
    fetchDone
  ]);





  const progressStep =
    stage === "freeText"
      ? quizQuestions.length
      : step;



  const showProgress =
    stage === "quiz" ||
    stage === "freeText";





  return (

    <section className="
      relative
      min-h-screen
      bg-[#05060b]
    ">


      {
        showProgress && (

          <div className="
            fixed
            left-0
            top-0
            z-40
            flex
            w-full
            justify-center
            bg-[#05060b]
            px-6
            pb-4
            pt-8
          ">

            <ProgressBar
              current={progressStep}
              total={5}
            />

          </div>

        )
      }






      {
        stage === "freeText" && (

          <div className="
            flex
            min-h-screen
            items-center
            justify-center
            px-6
          ">

            <FreeText

              answers={answers}

              onContinue={(text) => {

                setFreeText(text);

                setStage("thinking");

              }}

            />

          </div>

        )
      }






      {
        stage === "thinking" && (

          <ThinkingScreen

            title="VoyageAI is planning your trip"

            subtitle="
            Running semantic search and hybrid ranking...
            "

            pipeline={destinationPipeline}

            onFinished={() => {

              setAnimationDone(true);

            }}

          />

        )
      }






      {
        stage === "results" && (

          <ResultsPage

            recommendations={recommendations}

            error={fetchError}

            answers={answers}

          />

        )
      }







      {
        stage === "quiz" && (

          <div className="
            flex
            min-h-screen
            flex-col
            items-center
            justify-center
            px-6
            pt-24
    pb-8
          ">


            <div
              className="
    mx-auto
    flex
    w-full
    max-w-6xl
    justify-center
  "
            >


              <AnimatePresence mode="wait">


                <Question

                  key={step}

                  question={
                    quizQuestions[step].question
                  }


                  options={
                    quizQuestions[step].options
                  }


                  onAnswer={handleAnswer}

                />


              </AnimatePresence>


            </div>


          </div>

        )
      }



    </section>

  );

}