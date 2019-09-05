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
            var resultFile = @"C:\C:\Users\Sebastian Esser\Documents\Demos und Modelle\Alignment und LinearPlacement\SimpleLinearPlacement_Cypher.txt";
            //var sourceFile = @"C:\Users\Sebastian Esser\Documents\Demos und Modelle\Alignment\04-testfile-LineArcClothoid.ifc";
            //var resultFile = @"C:\C:\Users\Sebastian Esser\Documents\Demos und Modelle\Alignment\04-testfile-LineArcClothoid_Cypher.txt";

            // log
            Console.WriteLine("Location Source File: {0}", sourceFile);
            Console.WriteLine("Location Target File: {0} \n", resultFile);
            

            // call the parser
            var parser = new InstanceModel2Neo4jParser
            {
                SourceLocation = sourceFile,
                TargetLocation = resultFile
            };

            // run the parser
            var neo4jScript = parser.CreateNeo4jScript();

            // control log
            Console.WriteLine("Resulting Neo4j Commands are:");
            Console.Write(neo4jScript);

            // Safe result? 
            Console.WriteLine("Store result? Press 0 for no, 1 for yes");
            var userInput = Console.ReadLine();
            if (userInput == "1")
            {
                parser.StoreResult();
            }


            Console.WriteLine("--- End of App ---");
        }
    }
}