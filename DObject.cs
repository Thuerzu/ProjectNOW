namespace DObject
{
    public class DObject
    {
        public InvPlace invplace { get; set; }
        public ObjectId objectid { get; set; }
        public DType objecttype { get; set; }
        public DObject() : this(InvPlace.None, null) { }
        public DObject(InvPlace Invplace) : this(Invplace, null) { }
        public DObject(InvPlace Invplace, DType Dtype)
        {
            invplace = Invplace;
            objectid = new ObjectId();
            objecttype = Dtype;
        }
    }
}
