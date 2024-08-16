import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { CourseService } from '../course.service';
import { Course } from '../course.model';

@Component({
  selector: 'app-course-form',
  standalone: true,
  imports: [],
  templateUrl: './course-form.component.html',
  styleUrl: './course-form.component.scss',
})
export class CourseFormComponent implements OnInit {
  courseForm: FormGroup;
  isEditMode: boolean;

  constructor(
    private fb: FormBuilder,
    private courseService: CourseService,
    public dialogRef: MatDialogRef<CourseFormComponent>,
    @Inject(MAT_DIALOG_DATA) public data: Course
  ) {
    this.isEditMode = !!data?._id;
    this.courseForm = this.fb.group({
      university: ['', Validators.required],
      city: ['', Validators.required],
      country: ['', Validators.required],
      courseName: ['', Validators.required],
      courseDescription: ['', Validators.required],
      startDate: ['', Validators.required],
      endDate: ['', Validators.required],
      price: ['', [Validators.required, Validators.min(0)]],
      currency: ['', Validators.required],
    });
  }

  ngOnInit() {
    if (this.isEditMode) {
      this.courseForm.patchValue({
        university: this.data.university || '',
        city: this.data.city || '',
        country: this.data.country || '',
        courseName: this.data.courseName || '',
        courseDescription: this.data.courseDescription || '',
        startDate: this.data.startDate ? new Date(this.data.startDate) : '',
        endDate: this.data.endDate ? new Date(this.data.endDate) : '',
        price: this.data.price || '',
        currency: this.data.currency || '',
      });
    }
  }

  onSubmit() {
    if (this.courseForm.valid) {
      const course: Course = this.courseForm.value;
      if (this.isEditMode) {
        this.courseService.updateCourse(this.data._id!, course).subscribe(
          (updatedCourse) => {
            this.dialogRef.close(updatedCourse);
          },
          (error) => console.error('Error updating course', error)
        );
      } else {
        this.courseService.createCourse(course).subscribe(
          (newCourse) => {
            this.dialogRef.close(newCourse);
          },
          (error) => console.error('Error creating course', error)
        );
      }
    }
  }

  onCancel() {
    this.dialogRef.close();
  }
}
