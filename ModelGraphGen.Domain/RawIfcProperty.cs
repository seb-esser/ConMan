using System.Collections.Generic;

namespace ModelGraphGen.Domain
{
    public class RawIfcProperty
    {
        public string PName { get; set; }
        public string PVal_Simple { get; set; }
        public string PVal_Complex { get; set; }


        public RawIfcProperty()
        {
        }
    }
}