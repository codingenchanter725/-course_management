export interface Course {
  _id?: string;
  university: string;
  city: string;
  country: string;
  courseName: string;
  courseDescription: string;
  startDate: Date;
  endDate: Date;
  price: number;
  currency: string;
}
