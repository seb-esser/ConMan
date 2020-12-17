using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ModelGraphGen
{
    /// <summary>
    /// Interface to implement Import functions in any graph engine like Neo4J or GrGen
    /// </summary>
    interface IScriptGenerator
    {
        void GenerateNeo4JGraph();

        void GenerateGrGenGraph(); 
    }
}
