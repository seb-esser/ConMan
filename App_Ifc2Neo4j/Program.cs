using System;
using ModelGraphGen;

namespace App_Ifc2Neo4j
{
    internal class Program
    {
        private static void Main(string[] args)
        {
            Console.WriteLine("--- SampleApp for ModelGraphGen started. --- ");

            // define some paths
            var sourceFile = @"C:\Users\Sebastian Esser\Documents\Demos und Modelle\Alignment und LinearPlacement\SimpleLinearPlacement.ifc";
            var resultFile = @"C:\Users\Sebastian Esser\Documents\Demos und Modelle\Alignment und LinearPlacement\SimpleLinearPlacement_Cypher.txt";
            //var sourceFile = @"C:\Users\Sebastian Esser\Documents\Demos und Modelle\Alignment\04-testfile-LineArcClothoid.ifc";
            //var resultFile = @"C:\C:\Users\Sebastian Esser\Documents\Demos und Modelle\Alignment\04-testfile-LineArcClothoid_Cypher.txt";
            //var sourceFile = @"C:\Users\Sebastian Esser\Documents\Demos und Modelle\Gebäude\Haltepunkt_HpNeuhof_BSC_RosalieHolzinger_2019-03-21.ifc";
            //var resultFile = @"C:\C:\Users\Sebastian Esser\Documents\Demos und Modelle\Gebäude\Haltepunkt_HpNeuhof_BSC_RosalieHolzinger_2019-03-21_Cypher.txt";

            // log
            Console.WriteLine("Location Source File: {0}", sourceFile);
            Console.WriteLine("Location Target File: {0} \n", resultFile);
            

            // call the parser
            var parser = new Instance2Neo4jParser
            {
                SourceLocation = sourceFile,
                TargetLocation = resultFile
            };

            // run the parser
          //  var neo4JScript = parser.CreateNeo4JScript();
            parser.SendToDb();

            // control log
            //Console.WriteLine("Resulting Neo4j Commands are:");
            //Console.Write(neo4JScript);

            //// Safe result? 
            //Console.WriteLine("\n \n Store result? Press 0 for no, 1 for yes");
            //var userInput = Console.ReadLine();
            //if (userInput == "1")
            //{
            //    parser.StoreResult(neo4JScript);
            //}


            Console.WriteLine("--- End of App ---");
        }
    }
}