import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Course } from './course.model';

@Injectable({
  providedIn: 'root'
})
export class CourseService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  getCourses(page: number, perPage: number, search?: string): Observable<Course[]> {
    let url = `${this.apiUrl}/courses?page=${page}&per_page=${perPage}`;
    if (search) {
      url += `&search=${search}`;
    }
    return this.http.get<Course[]>(url);
  }

  createCourse(course: Course): Observable<Course> {
    return this.http.post<Course>(`${this.apiUrl}/courses`, course);
  }

  updateCourse(id: string, course: Course): Observable<Course> {
    return this.http.put<Course>(`${this.apiUrl}/courses/${id}`, course);
  }

  deleteCourse(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/courses/${id}`);
  }
}