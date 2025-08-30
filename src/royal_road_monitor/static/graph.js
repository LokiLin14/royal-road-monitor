// canvasId should be a string
// data should be of the form, the snapshots need to be increasing in time snapshot[0].time < snapshot[1].time < snapshot[2].time
// this.data = [
//     {
//         name: "RS",
//         snapshots: [
//             { rank: 5, time: new Date(2025, 5, 4, 3, 2, 1, 2) },
//             { rank: 2, time: new Date(2025, 5, 7, 3, 2, 1, 2) }
//         ]
//     },
// ];
class RankTimeGraphAlt {
    constructor(canvasId, data) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');

        this.data = data;
        let minDateTime = null;
        let maxDateTime = null;
        for (const watchedUrls of data) {
            for (const snapshot of watchedUrls.snapshots) {
                if (minDateTime == null) {
                    minDateTime = snapshot.time.getTime();
                    maxDateTime = snapshot.time.getTime();
                }
                minDateTime = Math.min(minDateTime, snapshot.time.getTime());
                maxDateTime = Math.max(maxDateTime, snapshot.time.getTime());
            }
        }
        let minDate = new Date(minDateTime ?? Date.now());
        let maxDate = new Date(maxDateTime ?? Date.now());
        minDate.setHours(0, 0, 0, 0);
        maxDate.setDate(maxDate.getDate() + 1);
        maxDate.setHours(0, 0, 0, 0);

        this.startTime = minDate;
        this.graphDurationInMilliseconds = maxDate.getTime() - minDate.getTime();

        // default settings
        this.mouseDown = false;
        this.margin = { top: 100, right: 60, bottom: 120, left: 120 };
        this.colors = [
            '#ff6b6b',
            '#1c8e22',
            '#dbc346',
            '#467fdb',
            '#37af9a'
        ];
        this.maxConnectionLengthInMilliseconds = 1000 * 60 * 60 * 24;

        this.draw();
        this.setupInteractivity();
    }

    recalculate() {
        // reset canvas width and height to display width and height
        const rect = this.canvas.getBoundingClientRect();
        const displayWidth = rect.width;
        const displayHeight = rect.height;

        // Account for device pixel ratio for sharp graphics
        const dpr = window.devicePixelRatio || 1;
        this.dpr = dpr;

        // Set internal resolution (higher for sharp graphics)
        this.canvas.width = displayWidth * dpr;
        this.canvas.height = displayHeight * dpr;

        // Calculate graph width
        this.width = this.canvas.width - this.margin.left - this.margin.right;
        this.height = this.canvas.height - this.margin.top - this.margin.bottom;

        // Calculate Y axis labels
        this.maxRank = 50;
        this.rankLines = 10;

        // Calculate X axis labels
        let millisecondsPerDay = 1000 * 60 * 60 * 24;
        let minimumPixelsPerLine = 300;
        let pixelsPerIncrement = millisecondsPerDay * this.width / this.graphDurationInMilliseconds;
        let minimumIncrementsPerLine = Math.ceil(minimumPixelsPerLine / pixelsPerIncrement);
        if (minimumIncrementsPerLine > 1 && minimumIncrementsPerLine < 7) {
            minimumIncrementsPerLine = 7;
        }
        if (minimumIncrementsPerLine > 7 && minimumIncrementsPerLine < 30) {
            minimumIncrementsPerLine = 30;
        }
        if (minimumIncrementsPerLine > 30 && minimumIncrementsPerLine < 120) {
            minimumIncrementsPerLine = 120;
        }
        if (minimumIncrementsPerLine > 120 && minimumIncrementsPerLine < 365) {
            minimumIncrementsPerLine = 365;
        }

        this.timeIncrementInMilliseconds = minimumIncrementsPerLine * millisecondsPerDay;

        let nextModuloDay = Math.ceil(this.startTime.getTime() / millisecondsPerDay / minimumIncrementsPerLine) * millisecondsPerDay * minimumIncrementsPerLine;
        this.firstLineTime = new Date(nextModuloDay);

        const remainingDuration = this.graphDurationInMilliseconds - (this.firstLineTime.getTime() - this.startTime.getTime());
        this.timeLines = Math.floor(remainingDuration / this.timeIncrementInMilliseconds);
    }

    xOfDate(currentTime) {
        let offsetFromStartInMilli = currentTime.getTime() - this.startTime.getTime();
        return this.width * (offsetFromStartInMilli / this.graphDurationInMilliseconds) + this.margin.left;
    }

    yOfRank(rank) {
        return this.margin.top + this.height / this.maxRank * rank;
    }

    draw() {
        this.recalculate();

        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Y-axis labels (ranks)
        this.ctx.textAlign = 'right';
        this.ctx.textBaseline = 'middle';
        this.ctx.font = 'bold 30px Arial';
        this.ctx.strokeStyle = '#d19494';
        this.ctx.lineWidth = 2;

        const rankStep = this.maxRank / this.rankLines;
        for (let i = 0; i <= this.rankLines; i++) {
            const rank = i * rankStep;
            const y = i * (this.height / this.rankLines) + this.margin.top;
            this.ctx.fillText(rank.toString(), this.margin.left - 10, y);

            this.ctx.beginPath();
            this.ctx.moveTo(this.margin.left, y);
            this.ctx.lineTo(this.margin.left + this.width, y);
            this.ctx.stroke();
        }

        // Y-axis title
        this.ctx.save();
        this.ctx.translate(20, this.margin.top + this.height / 2);
        this.ctx.rotate(-Math.PI / 2);
        this.ctx.textAlign = 'center';
        this.ctx.font = 'bold 40px Arial';
        this.ctx.fillText('Rank (lower is better)', 0, 0);
        this.ctx.restore();

        // X-axis labels (times)
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'top';
        this.ctx.font = 'bold 30px Arial';
        this.ctx.strokeStyle = '#d19494';
        this.ctx.lineWidth = 2;

        for (let i = 0; i <= this.timeLines; i++) {
            let currentTime = new Date(this.firstLineTime.getTime() + i * this.timeIncrementInMilliseconds);

            const x = this.xOfDate(currentTime);

            const year = String(currentTime.getFullYear());
            const month = String(currentTime.getMonth() + 1); // +1 because months are 0-indexed
            const day = String(currentTime.getDate());
            const hour = String(currentTime.getHours()).padStart(2, '0');
            const minute = String(currentTime.getMinutes()).padStart(2, '0');

            const dateStr = `${year}/${month}/${day}`;
            const timeStr =  `${hour}:${minute}`;

            this.ctx.fillText(dateStr, x, this.margin.top + this.height + 15);
            this.ctx.fillText(timeStr, x, this.margin.top + this.height + 45);

            this.ctx.beginPath();
            this.ctx.moveTo(x, this.margin.top);
            this.ctx.lineTo(x, this.margin.top + this.height);
            this.ctx.stroke();
        }

        for (const [index, watchedUrl] of this.data.entries()) {
            let previousPoint = null;
            for (const snapshot of watchedUrl.snapshots) {
                const x = this.xOfDate(snapshot.time);
                const y = this.yOfRank(snapshot.rank);

                if (x < this.margin.left || x > this.margin.left + this.width) {
                    continue;
                }

                // Point shadow
                this.ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
                this.ctx.beginPath();
                this.ctx.arc(x + 2, y + 2, 12, 0, 2 * Math.PI);
                this.ctx.fill();

                // Draw the datapoints
                this.ctx.fillStyle = this.colors[index % this.colors.length];
                this.ctx.beginPath();
                this.ctx.arc(x, y, 10, 0, 2 * Math.PI);
                this.ctx.fill();

                // Point border
                this.ctx.strokeStyle = '#ffffff';
                this.ctx.lineWidth = 4;
                this.ctx.stroke();
            }
            // Draw lines to connect the points
            this.ctx.lineWidth = 8;
            this.ctx.strokeStyle = this.colors[index % this.colors.length];
            for (let i = 0; i + 1 < watchedUrl.snapshots.length; i++) {
                const left = watchedUrl.snapshots[i];
                const right = watchedUrl.snapshots[i + 1];
                let leftX = this.xOfDate(left.time);
                let leftY = this.yOfRank(left.rank);
                let rightX = this.xOfDate(right.time);
                let rightY = this.yOfRank(right.rank);
                // continue in the case that the line segment isn't in the plotted area at all
                if (rightX < this.margin.left || leftX > this.margin.left + this.width) {
                    continue;
                }
                // continue in the case that their times differ by more than the allowed amount
                if (right.time.getTime() - left.time.getTime() > this.maxConnectionLengthInMilliseconds) {
                    continue;
                }
                // Snap points to border if necessary
                const dydx = (rightY - leftY) / (rightX - leftX);
                if (leftX < this.margin.left) {
                    const diff = this.margin.left - leftX;
                    leftX += diff;
                    leftY += dydx * diff;
                }
                if (rightX > this.margin.left + this.width) {
                    const diff = this.margin.left + this.width - rightX;
                    rightX += diff;
                    rightY += dydx * diff;
                }
                this.ctx.beginPath();
                this.ctx.moveTo(leftX, leftY);
                this.ctx.lineTo(rightX, rightY);
                this.ctx.stroke();
            }
        }

        // Draw the title and legend
        this.ctx.font = 'bold 32px Arial';
        this.ctx.textAlign = 'left';
        let titles = this.data.map((x) => x.name);
        for (let i = 0; i < titles.length; i++) {
            let x = this.width / (titles.length + 1) * (1 + i);

            this.ctx.fillStyle = this.colors[i % this.colors.length];
            this.ctx.beginPath();
            this.ctx.rect(x - 80, 50, 60, 32);
            this.ctx.fill();

            this.ctx.strokeStyle = '#ffffff';
            this.ctx.lineWidth = 4;
            this.ctx.stroke();

            this.ctx.fillStyle = '#2c3e50';
            this.ctx.fillText(titles[i], x, 50);
        }

        // Draw left and bottom line
        this.ctx.strokeStyle = '#2c3e50';
        this.ctx.fillStyle = '#2c3e50';
        this.ctx.lineWidth = 6;

        // Y-axis
        this.ctx.beginPath();
        this.ctx.moveTo(this.margin.left, this.margin.top - this.ctx.lineWidth / 2);
        this.ctx.lineTo(this.margin.left, this.margin.top + this.height + this.ctx.lineWidth / 2);
        this.ctx.stroke();

        // X-axis
        this.ctx.beginPath();
        this.ctx.moveTo(this.margin.left - this.ctx.lineWidth / 2, this.margin.top + this.height);
        this.ctx.lineTo(this.margin.left + this.width + this.ctx.lineWidth / 2, this.margin.top + this.height);
        this.ctx.stroke();
    }

    setupInteractivity() {
        this.canvas.addEventListener('mousedown', (e) => {
            this.mouseDown = true;
        });
        this.canvas.addEventListener('mousemove', (e) => {
            if (this.mouseDown) {
                const movementX = e.movementX * this.dpr;
                const offsetTimeInMilli = (movementX / this.width) * this.graphDurationInMilliseconds;
                this.startTime = new Date(this.startTime.getTime() - offsetTimeInMilli);
                this.draw();
            }
        });
        this.canvas.addEventListener('mouseup', () => {
            this.mouseDown = false;
        });
        this.canvas.addEventListener('mouseleave', () => {
            if (this.mouseDown) {
                this.mouseDown = false;
            }
        });
        this.canvas.addEventListener('wheel', (e) => {
            e.preventDefault(); // Prevent page scroll
            if (!this.mouseDown) {
                const changeRatio = Math.pow(105 / 100, e.deltaY / 100);
                const timeFromStart = (e.offsetX * this.dpr - this.margin.left) * this.graphDurationInMilliseconds / this.width;

                this.graphDurationInMilliseconds = this.graphDurationInMilliseconds * changeRatio;
                this.startTime = new Date(this.startTime.getTime() + (timeFromStart - timeFromStart * changeRatio));
                this.draw();
            }
        });
    }
}