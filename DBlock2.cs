using System;

namespace DGeometrics
{
    public class DBlock2 : IComparable // class for building blocks
    {
        public int X { get; set; } // center coord X
        public int Y { get; set; } // center coord Y
        public int Radius { get; private set; } // Radius
        public int left_X { get; private set; } // left side X
        public int right_X { get; private set; } // right side X
        public int up_Y { get; private set; } // up side Y
        public int down_Y { get; private set; } // down side Y

        public DBlock2() : this(0, 0, 32) { } // see DBlock2
        public DBlock2(int x, int y) : this(x, y, 32) { } // see DBlock2
        public DBlock2(DPoint2 point) : this(point.X, point.Y, 32) { } // see DBlock2
        public DBlock2(DBlock2 block2) : this(block2.X, block2.Y, block2.Radius) { } // see DBlock2
        public DBlock2(int x, int y, int radius) // constructor of DBlock2
        {
            X = x;
            Y = y;
            Radius = radius;
            this.GetCoords();
        }

        private void GetCoords() // returns the coords of the perimeter
        {
            left_X = X - Radius;
            right_X = X + Radius;
            up_Y = Y - Radius;
            down_Y = Y + Radius;
        }

        public void Move(DPoint2 point) => Move(point.X, point.Y); // see Move
        public void Move(int x, int y) // moves the block
        {
            X += x;
            Y += y;
            this.GetCoords();
        }
        public void ChangeSize(int radius) // changes the radius of the block if it is valid
        {
            if (radius % 32 == 0)
            {
                Radius = radius;
                this.GetCoords();
            }
            else throw new InvalidCastException("That's not a valid value.");
        }
        public DPoint2 GetCenterPoint() // returns the center Point as a DPoint2
        { 
            return new DPoint2(X, Y); 
        }

        public int CompareTo(object obj) // compares two Blocks (IComperable)
        {
            if (obj == null) return 1;
            DBlock2 point = obj as DBlock2;
            int self = this.GetArea();
            int point_ = point.GetArea();
            if (self > point_) return 1;
            else if (point_ > self) return -1;
            else if (self == point_) return 0;
            throw new InvalidCastException("An error occured");
        }

        public int GetArea() // returns the Area of the Block
        {
            return (int)Math.Pow((Radius * 2), 2);
        }
    }
}
