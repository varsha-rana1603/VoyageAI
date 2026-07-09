"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  Brain,
  Sparkles,
  Globe2,
  BarChart3,
  CheckCircle2,
  Loader2,
} from "lucide-react";


/* -----------------------------
   Destination Recommendation Flow
------------------------------ */

export const destinationPipeline = [
  {
    stage: "profiling",
    icon: Brain,
    title: "Understanding your travel personality...",
    completed: "Preferences extracted",
  },
  {
    stage: "embedding",
    icon: Sparkles,
    title: "Generating semantic embedding...",
    completed: "User profile vector created",
  },
  {
    stage: "searching",
    icon: Globe2,
    title: "Comparing against destinations...",
    completed: "Top candidates found",
  },
  {
    stage: "ranking",
    icon: BarChart3,
    title: "Calculating hybrid ranking...",
    completed: "Scores computed",
  },
  {
    stage: "finalizing",
    icon: CheckCircle2,
    title: "Generating explainable recommendations...",
    completed: "Ready!",
  },
];

export const stayPipeline = [

{
 stage:"searching",
 icon:Globe2,
 title:"Searching local accommodations...",
 completed:"Nearby stays discovered",
},

{
 stage:"enriching",
 icon:Sparkles,
 title:"Analyzing views, comfort and amenities...",
 completed:"Stay profiles created",
},

{
 stage:"embedding",
 icon:Brain,
 title:"Understanding your travel preferences...",
 completed:"Travel profile matched",
},

{
 stage:"matching",
 icon:BarChart3,
 title:"Ranking stays using AI matching...",
 completed:"Scores computed",
},

{
 stage:"finalizing",
 icon:CheckCircle2,
 title:"Preparing your stay recommendations...",
 completed:"Almost ready",
},

{
 stage:"complete",
 icon:CheckCircle2,
 title:"Your stay recommendations are ready!",
 completed:"Ready!",
}

];


interface PipelineStep {
  stage: string;
  icon: any;
  title: string;
  completed: string;
}


interface ThinkingScreenProps {
  title: string;
  subtitle: string;
  pipeline: PipelineStep[];
  currentStage: string;
  progress: number;
  onFinished: () => void;
}



export default function ThinkingScreen({
  title,
  subtitle,
  pipeline,
  currentStage,
  progress,
  onFinished,
}: ThinkingScreenProps) {


  const currentIndex =
    pipeline.findIndex(
      step => step.stage === currentStage
    );


  if(progress === 100){
    setTimeout(() => {
      onFinished();
    },800);
  }



  return (

    <section
      className="
      flex
      min-h-screen
      items-center
      justify-center
      bg-[#05060b]
      px-6
      "
    >

      <motion.div

        initial={{
          opacity:0,
          scale:0.95
        }}

        animate={{
          opacity:1,
          scale:1
        }}

        className="
        w-full
        max-w-3xl
        rounded-3xl
        border
        border-white/10
        bg-white/5
        p-10
        backdrop-blur-2xl
        "
      >


        <h1
        className="
        mb-3
        text-center
        text-4xl
        font-bold
        "
        >
          {title}
        </h1>


        <p
        className="
        mb-8
        text-center
        text-zinc-400
        "
        >
          {subtitle}
        </p>



        {/* Progress */}

        <div
        className="
        mb-10
        h-2
        overflow-hidden
        rounded-full
        bg-white/10
        "
        >

          <motion.div

          animate={{
            width:`${progress}%`
          }}

          className="
          h-full
          rounded-full
          bg-gradient-to-r
          from-cyan-400
          to-blue-500
          "

          />

        </div>



        <p
        className="
        mb-10
        text-center
        text-cyan-400
        "
        >
          {progress}% complete
        </p>





        <div className="space-y-8">


        {
          pipeline.map((step,index)=>{


            const Icon = step.icon;


            const done =
              index < currentIndex ||
              progress === 100;


            const active =
              index === currentIndex;



            return (

              <motion.div

              key={step.stage}

              animate={{
                opacity:1,
                y:0
              }}

              initial={{
                opacity:0,
                y:15
              }}

              className="
              flex
              items-start
              gap-5
              "

              >


                <div className="mt-1">


                {
                  done ?

                  (

                  <CheckCircle2
                  size={28}
                  className="text-green-400"
                  />

                  )

                  :

                  active ?

                  (

                  <Loader2
                  size={28}
                  className="
                  animate-spin
                  text-cyan-400
                  "
                  />

                  )

                  :

                  (

                  <Icon
                  size={28}
                  className="text-zinc-600"
                  />

                  )

                }


                </div>



                <div className="flex-1">


                <p
                className={`
                text-xl
                ${
                  done || active
                  ? "text-white"
                  : "text-zinc-500"
                }
                `}
                >

                  {step.title}

                </p>




                {
                  done &&

                  <p
                  className="
                  mt-2
                  text-green-400
                  "
                  >
                    ✓ {step.completed}
                  </p>

                }




                {
                  active &&

                  <motion.div

                  initial={{
                    width:0
                  }}

                  animate={{
                    width:"100%"
                  }}

                  transition={{
                    duration:1
                  }}

                  className="
                  mt-4
                  h-[3px]
                  rounded-full
                  bg-gradient-to-r
                  from-cyan-400
                  via-blue-500
                  to-cyan-400
                  "

                  />

                }



                </div>


              </motion.div>

            )

          })
        }


        </div>



      </motion.div>


    </section>

  );
}