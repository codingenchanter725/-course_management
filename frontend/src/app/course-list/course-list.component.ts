import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { CourseService } from '../course.service';
import { Course } from '../course.model';
import { CourseFormComponent } from '../course-form/course-form.component';

@Component({
  selector: 'app-course-list',
  standalone: true,
  imports: [],
  templateUrl: './course-list.component.html',
  styleUrl: './course-list.component.scss',
})
export class CourseListComponent implements OnInit {
  courses: Course[] = [];
  currentPage = 1;
  pageSize = 10;
  totalCourses = 0;

  constructor(
    private courseService: CourseService,
    private dialog: MatDialog
  ) {}

  ngOnInit() {
    this.loadCourses();
  }

  loadCourses(search: string = '') {
    this.courseService
      .getCourses(this.currentPage, this.pageSize, search)
      .subscribe(
        (courses: Course[]) => {
          this.courses = courses;
          this.totalCourses = courses.length; // This should be the total count from the backend
        },
        (error) => console.error('Error loading courses', error)
      );
  }

  onPageChange(event: any) {
    this.currentPage = event.pageIndex + 1;
    this.pageSize = event.pageSize;
    this.loadCourses();
  }

  onSearch(searchTerm: string) {
    this.currentPage = 1;
    this.loadCourses(searchTerm);
  }

  openCourseForm(course?: Course) {
    const dialogRef = this.dialog.open(CourseFormComponent, {
      width: '500px',
      data: course || {},
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.loadCourses();
      }
    });
  }

  deleteCourse(id: string) {
    if (confirm('Are you sure you want to delete this course?')) {
      this.courseService.deleteCourse(id).subscribe(
        () => this.loadCourses(),
        (error) => console.error('Error deleting course', error)
      );
    }
  }
}
