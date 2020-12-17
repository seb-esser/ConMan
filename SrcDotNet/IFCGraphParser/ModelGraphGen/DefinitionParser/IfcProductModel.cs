using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ModelGraphGen.DefinitionParser
{
    /// <summary>
    /// represents the Product model level which is composed by components of the Ifc Meta Model
    /// </summary>
    class IfcProductModel : IParser
    {
        /// <inheritdoc />
        public string Parse(string fileDirectory)
        {
            // Read a text file line by line.
            var lines = File.ReadAllText(fileDirectory);
            var splitted =  lines.Split(new [] {"TYPE","ENTITY"}, StringSplitOptions.RemoveEmptyEntries);
            

            return null; 
        }
    }
}
