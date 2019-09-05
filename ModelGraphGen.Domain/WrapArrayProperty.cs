using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ModelGraphGen.Domain
{
    public class WrapArrayProperty : AbstractProperty
    {
        public List<ArrayProperty> ArrayProperties;

        public WrapArrayProperty()
        {
            ArrayProperties = new List<ArrayProperty>();
        }
        
    }
}
