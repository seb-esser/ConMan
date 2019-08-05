using System.Collections.Generic;

namespace ModelGraphGen.Domain
{
    public class RawIfcProperty
    {
        public string PName { get; set; }
        public string PVal_Normal { get; set; }
        public string PVal_Reference { get; set; }
        public List<RawIfcProperty> ReferencedEntities { get; set; }
        public Vec2D Vec2D { get; set; }
        public Vec3D Vec3D { get; set; }

        public RawIfcProperty()
        {  
            ReferencedEntities = new List<RawIfcProperty>();
        }
    }
}